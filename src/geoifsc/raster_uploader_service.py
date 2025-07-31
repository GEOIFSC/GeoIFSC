"""
Serviço para upload de raster para PostGIS com fallback automático.
"""

import os
import sys
import threading
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

from PyQt5.QtCore import QObject, pyqtSignal
from qgis.core import QgsApplication

from .raster_upload_params import RasterUploadParams
from .geoifsc_utils import (
    find_executable, get_postgres_possible_paths, run_subprocess_with_cancel,
    fetch_existing_table_names, compute_next_suffix
)


class RasterUploaderService(QObject):
    """Serviço para upload de raster para PostGIS."""
    
    progress_updated = pyqtSignal(int)
    file_upload_started = pyqtSignal(str)
    file_upload_success = pyqtSignal(str)
    file_upload_error = pyqtSignal(str, str)
    upload_completed = pyqtSignal()
    log_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # ─── INJEÇÃO DO QGIS_BIN NO PATH ─────────────────────────────────────────
        try:
            # prefixPath é algo como "C:/Program Files/QGIS 3.xx/apps/qgis-ltr"
            prefix = QgsApplication.prefixPath()
            apps_dir = os.path.dirname(prefix)           # ".../apps"
            root_dir = os.path.dirname(apps_dir)         # ".../QGIS 3.xx" ou "C:/OSGeo4W64"
            # Possíveis pastas "bin" onde o QGIS/OSGeo4W instala os executáveis
            for p in (
                os.path.join(apps_dir, 'bin'),           # standalone installer
                os.path.join(root_dir, 'bin')            # OSGeo4W64/bin
            ):
                if os.path.isdir(p):
                    os.environ['PATH'] = p + os.pathsep + os.environ.get('PATH', '')
                    self._log(f"Adicionado ao PATH: {p}")
        except Exception as e:
            self._log(f"Aviso: Não foi possível estender PATH do QGIS: {e}")
        # ─────────────────────────────────────────────────────────────────────────
        
        self._is_cancelled = False
        self._upload_thread: Optional[threading.Thread] = None
    
    def _log(self, message: str):
        """Emite mensagem de log com timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_message.emit(formatted_message)
    
    def upload_rasters(self, params: RasterUploadParams):
        """Inicia upload de rasters em thread separada."""
        if self._upload_thread and self._upload_thread.is_alive():
            self._log("Upload já está em andamento")
            return
        
        self._is_cancelled = False
        self._upload_thread = threading.Thread(
            target=self._upload_rasters_worker,
            args=(params,)
        )
        self._upload_thread.daemon = True
        self._upload_thread.start()
    
    def cancel_upload(self):
        """Cancela o upload em andamento."""
        self._is_cancelled = True
        self._log("Upload cancelado pelo usuário")
    
    def _upload_rasters_worker(self, params: RasterUploadParams):
        """Worker thread para upload de rasters."""
        self._log(f"Iniciando upload de {len(params.raster_files)} arquivos")
        
        total_files = len(params.raster_files)
        
        for i, raster_file in enumerate(params.raster_files):
            if self._is_cancelled:
                self._log("Upload cancelado")
                break
            
            # Calcula progresso
            progress = int((i / total_files) * 100)
            self.progress_updated.emit(progress)
            
            # Nome da tabela baseado no basename do arquivo
            file_name = Path(raster_file).stem
            table_name = f"{params.table_name_prefix}{file_name}" if params.table_name_prefix else file_name
            
            self.file_upload_started.emit(raster_file)
            self._log(f"Enviando {file_name} → {table_name}")
            
            try:
                success = self._upload_single_raster(
                    raster_file, table_name, params
                )
                
                if success:
                    self.file_upload_success.emit(raster_file)
                    self._log(f"✓ {file_name} enviado com sucesso")
                else:
                    self.file_upload_error.emit(raster_file, "Falha no upload")
                    self._log(f"✗ Falha ao enviar {file_name}")
                    
            except Exception as e:
                error_msg = str(e)
                self.file_upload_error.emit(raster_file, error_msg)
                self._log(f"✗ Erro ao enviar {file_name}: {error_msg}")
        
        # Progresso final
        if not self._is_cancelled:
            self.progress_updated.emit(100)
            self._log("Upload concluído")
        
        self.upload_completed.emit()
    
    def _determine_upload_mode(self, file_size: int) -> Tuple[str, str, int]:
        """
        Determina o modo de upload, tamanho de tile e timeout com base no tamanho do arquivo.

        Args:
            file_size: Tamanho do arquivo em bytes.

        Returns:
            Uma tupla contendo o modo de upload, tamanho de tile e timeout.
        """
        if file_size <= 100 * 1024 * 1024:  # ≤ 100 MB
            return "SQL+psql", "512x512", 300  # Mudado de "auto" para "512x512" para melhor performance
        elif file_size <= 500 * 1024 * 1024:  # 100 MB < tamanho ≤ 500 MB
            return "Direct load", "512x512", 600
        else:  # > 500 MB
            return "Out-of-DB", "512x512", 1200

    def _upload_single_raster(
        self,
        raster_file: str,
        table_name: str,
        params: RasterUploadParams
    ) -> bool:
        """
        Carrega um único raster usando raster2pgsql e psql.
        """
        # Valida se o arquivo raster existe
        if not os.path.exists(raster_file):
            self._log(f"ERRO: Arquivo raster não encontrado: {raster_file}")
            return False

        # Obtém o tamanho do arquivo
        try:
            file_size = os.path.getsize(raster_file)
            self._log(f"Tamanho do arquivo: {file_size / (1024*1024):.2f} MB")
        except Exception as e:
            self._log(f"ERRO: Não foi possível obter tamanho do arquivo: {e}")
            return False

        # Determina o modo de upload, tamanho de tile e timeout
        mode, tile_size, timeout = self._determine_upload_mode(file_size)
        self._log(f"Modo de upload: {mode}, Tamanho de tile: {tile_size}, Timeout: {timeout}s")

        # Localiza os executáveis
        raster2pgsql = params.raster2pgsql_path or find_executable("raster2pgsql", get_postgres_possible_paths("raster2pgsql"))
        psql = params.psql_path or find_executable("psql", get_postgres_possible_paths("psql"))

        if not raster2pgsql or not os.path.exists(raster2pgsql):
            self._log("ERRO: raster2pgsql não encontrado!")
            return False

        if not psql or not os.path.exists(psql):
            self._log("ERRO: psql não encontrado!")
            return False

        # Logs detalhados dos executáveis encontrados
        self._log(f"Usando raster2pgsql: {raster2pgsql}")
        self._log(f"Usando psql: {psql}")
        
        # Verificação de GDAL (diagnóstico)
        self._check_gdal_environment()
        
        # Verificação do arquivo raster com gdalinfo
        self._check_raster_file_info(raster_file)

        # Configura o comando raster2pgsql
        cmd_r2p = [
            raster2pgsql,
            "-c", "-d",
            "-s", str(params.srid),
            "-t", tile_size,
            "-I", "-C",
            raster_file,  # Removidas as aspas extras
            f"{params.connection.schema}.{table_name}"
        ]

        if mode == "Out-of-DB":
            cmd_r2p.append("-M")

        env = os.environ.copy()
        env["PGPASSWORD"] = params.connection.password

        # Adiciona logs para o comando completo e timeout
        self._log(f"Comando completo: {' '.join(cmd_r2p)}")
        self._log(f"Timeout configurado: {timeout}s")

        # Executa o raster2pgsql
        self._log(f"Executando raster2pgsql: {' '.join(cmd_r2p)}")
        code, sql, err = run_subprocess_with_cancel(
            command=cmd_r2p,
            env=env,
            cancel_check_func=params.cancel_check_func,
            timeout=timeout
        )

        if code != 0:
            self._log(f"ERRO: raster2pgsql falhou com código de saída: {code}")
            if err:
                self._log(f"STDERR: {err}")
            return False

        self._log(f"✓ SQL gerado com sucesso ({len(sql)} caracteres)")
        
        # Log de uma amostra do SQL para diagnóstico
        self._log_sql_sample(sql)

        # Configura o comando psql
        cmd_psql = [
            psql,
            "-h", params.connection.host,
            "-p", str(params.connection.port),
            "-U", params.connection.username,
            "-d", params.connection.database,
            "-q"
        ]

        # Executa o psql
        self._log(f"Executando psql: {' '.join(cmd_psql)}")
        self._log(f"Enviando SQL de {len(sql)} caracteres + COMMIT para o banco")
        
        code, out, err = run_subprocess_with_cancel(
            command=cmd_psql,
            env=env,
            input_text=sql + "\nCOMMIT;",
            cancel_check_func=params.cancel_check_func,
            timeout=60  # Timeout fixo para psql
        )

        if code != 0:
            self._log(f"ERRO: psql falhou com código de saída: {code}")
            if err:
                self._log(f"STDERR: {err}")
            if out:
                self._log(f"STDOUT: {out}")
            return False
        
        self._log("✓ SQL executado com sucesso no banco de dados")

        self._log("Upload concluído com sucesso.")
        return True
    
    def _check_gdal_environment(self):
        """Verifica se o GDAL está instalado e acessível."""
        try:
            # Testa gdalinfo --version
            code, output, err = run_subprocess_with_cancel(
                command=["gdalinfo", "--version"],
                env=os.environ.copy(),
                timeout=10
            )
            if code == 0:
                self._log(f"GDAL encontrado: {output.strip()}")
            else:
                self._log(f"GDAL não encontrado ou com problemas: {err}")
        except Exception as e:
            self._log(f"Erro ao verificar GDAL: {e}")
    
    def _check_raster_file_info(self, raster_file: str):
        """Verifica informações do arquivo raster usando gdalinfo."""
        try:
            # Testa gdalinfo no arquivo
            code, output, err = run_subprocess_with_cancel(
                command=["gdalinfo", raster_file],  # Removidas as aspas extras
                env=os.environ.copy(),
                timeout=30
            )
            if code == 0:
                # Extrai informações importantes
                lines = output.split('\n')
                for line in lines[:10]:  # Primeiras 10 linhas
                    if any(keyword in line for keyword in ['Size is', 'Coordinate System', 'EPSG', 'Driver:']):
                        self._log(f"Info raster: {line.strip()}")
            else:
                self._log(f"Não foi possível obter informações do raster via gdalinfo: {err}")
        except Exception as e:
            self._log(f"Erro ao verificar arquivo raster: {e}")
    
    def _log_sql_sample(self, sql: str):
        """Log de uma amostra do SQL gerado."""
        if len(sql) > 1000:
            # Mostra início e fim do SQL
            start = sql[:300]
            end = sql[-300:]
            self._log(f"SQL início: {start}")
            self._log(f"SQL fim: {end}")
        else:
            self._log(f"SQL completo: {sql}")
    
    
    
    def _resolve_table_name(self, base_name: str, params: RasterUploadParams) -> str:
        """Resolve nome final da tabela considerando flag de substituição."""
        if params.overwrite:
            # Se overwrite=True, usa nome original (será recriada com -d)
            self._log(f"Modo sobrescrita ativado: {base_name} será recriada")
            return base_name
        
        # Se overwrite=False, verifica se tabela existe e incrementa sufixo
        return self._get_unique_table_name(base_name, params)
    
    def _get_unique_table_name(self, base_name: str, params: RasterUploadParams) -> str:
        """Gera nome único de forma otimizada usando uma única query."""
        try:
            # Busca de forma otimizada
            existing = fetch_existing_table_names(params.connection, base_name)
            unique_name = compute_next_suffix(base_name, existing)
            
            if unique_name == base_name:
                self._log(f"Tabela {base_name} não existe, usando nome original")
            else:
                self._log(f"Nome único encontrado: {unique_name}")
            
            return unique_name
            
        except Exception as e:
            self._log(f"Erro na resolução do nome da tabela: {e}, usando nome original")
            return base_name
    
    def find_raster2pgsql(self) -> Optional[str]:
        """Localiza o executável raster2pgsql (plugin-local primeiro)."""
        possible_paths = get_postgres_possible_paths("raster2pgsql")
        executable = find_executable("raster2pgsql", possible_paths)
        
        if executable:
            # Verifica se é do plugin
            plugin_bin = os.path.join(os.path.dirname(__file__), 'bin')
            if executable.startswith(plugin_bin):
                self._log(f"Usando raster2pgsql do plugin: {executable}")
            else:
                self._log(f"Usando raster2pgsql do sistema: {executable}")
        else:
            self._log("⚠️ raster2pgsql não encontrado. Instale PostgreSQL ou adicione os executáveis à pasta bin/ do plugin")
            
        return executable
    
    def find_psql(self) -> Optional[str]:
        """Localiza o executável psql (plugin-local primeiro)."""
        possible_paths = get_postgres_possible_paths("psql")
        executable = find_executable("psql", possible_paths)
        
        if executable:
            # Verifica se é do plugin
            plugin_bin = os.path.join(os.path.dirname(__file__), 'bin')
            if executable.startswith(plugin_bin):
                self._log(f"Usando psql do plugin: {executable}")
            else:
                self._log(f"Usando psql do sistema: {executable}")
        else:
            self._log("⚠️ psql não encontrado. Instale PostgreSQL ou adicione os executáveis à pasta bin/ do plugin")
            
        return executable




