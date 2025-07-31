"""
Utilitários gerais para o plugin GeoIFSC.

Este módulo contém funções auxiliares reutilizáveis em todo o projeto.
"""
import os
import shutil
import subprocess
import time
import re
from typing import List, Optional, Tuple

import psycopg2
from .raster_upload_params import ConnectionParams


def find_executable(exe_name: str, possible_paths: List[str]) -> Optional[str]:
    """
    Localiza um executável seguindo a ordem de prioridade:
    1) Plugin-local bin directory
    2) PATH do sistema
    3) Caminhos padrões do PostgreSQL

    Args:
        exe_name: Nome do executável (ex: "raster2pgsql", "psql")
        possible_paths: Lista de caminhos possíveis onde procurar

    Returns:
        Caminho completo do executável encontrado ou None se não encontrado
    """
    # 1) Plugin-local bin directory
    plugin_root = os.path.dirname(__file__)  # .../src/geoifsc
    plugin_bin = os.path.join(plugin_root, 'bin')
    exe_file = f"{exe_name}.exe" if not exe_name.endswith('.exe') else exe_name
    candidate = os.path.join(plugin_bin, exe_file)
    if os.path.isfile(candidate):
        return candidate

    # 2) PATH do sistema
    exe_path = shutil.which(exe_name)
    if exe_path:
        return exe_path

    # 3) Caminhos padrões do PostgreSQL
    for path in possible_paths:
        if os.path.isfile(path):
            return path

    return None


def get_postgres_possible_paths(exe_name: str) -> List[str]:
    """
    Retorna lista de caminhos possíveis para executáveis PostgreSQL no Windows.

    Args:
        exe_name: Nome do executável (sem extensão .exe)

    Returns:
        Lista de caminhos possíveis
    """
    exe_file = f"{exe_name}.exe"
    versions = ["17", "16", "15", "14", "13", "12", "11", "10"]

    possible_paths: List[str] = []
    # Program Files
    for version in versions:
        possible_paths.append(f"C:\\Program Files\\PostgreSQL\\{version}\\bin\\{exe_file}")
    # Program Files (x86)
    for version in versions:
        possible_paths.append(f"C:\\Program Files (x86)\\PostgreSQL\\{version}\\bin\\{exe_file}")

    return possible_paths


def run_subprocess(command: List[str], env: dict, input_text: Optional[str] = None) -> Tuple[int, str, str]:
    """
    Executa comando subprocess com configurações padronizadas.

    Args:
        command: Lista com comando e argumentos
        env: Dicionário de variáveis de ambiente
        input_text: Texto opcional para enviar via stdin

    Returns:
        Tupla (returncode, stdout, stderr)
    """
    kwargs = {
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'text': True,
        'env': env
    }
    if input_text is not None:
        kwargs['input'] = input_text
    if os.name == 'nt':
        kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
    try:
        result = subprocess.run(command, **kwargs)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def run_subprocess_with_cancel(
    command: List[str],
    env: dict,
    cancel_check_func=None,
    input_text: Optional[str] = None,
    timeout: int = 300
) -> Tuple[int, str, str]:
    """
    Executa comando subprocess com suporte a cancelamento e timeout.

    Args:
        command: Lista com comando e argumentos
        env: Dicionário de variáveis de ambiente
        cancel_check_func: Função que retorna True se deve cancelar
        input_text: Texto opcional para enviar via stdin
        timeout: Timeout em segundos (padrão: 5 minutos)

    Returns:
        Tupla (returncode, stdout, stderr)
        -2 se cancelado, -3 se timeout
    """
    kwargs = {
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'env': env,
        'text': True
    }
    if os.name == 'nt':
        kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
    try:
        process = subprocess.Popen(command, **kwargs)
        if input_text is not None:
            stdout, stderr = process.communicate(input=input_text, timeout=timeout)
        else:
            start = time.time()
            while process.poll() is None:
                if cancel_check_func and cancel_check_func():
                    process.terminate()
                    try:
                        process.wait(5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    return -2, "", "Cancelado pelo usuário"
                if time.time() - start > timeout:
                    process.terminate()
                    try:
                        process.wait(5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    return -3, "", f"Timeout após {timeout} segundos"
                time.sleep(0.1)
            stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        return -3, "", f"Timeout após {timeout} segundos"
    except Exception as e:
        return -1, "", str(e)


def fetch_existing_table_names(params: ConnectionParams, base_name: str) -> List[str]:
    """
    Retorna todos os nomes de tabela no schema que começam com base_name.
    """
    query = (
        "SELECT table_name"
        " FROM information_schema.tables"
        " WHERE table_schema = %(schema)s"
        " AND table_name LIKE %(pattern)s;"
    )
    pattern = f"{base_name}%"
    conn = None
    try:
        conn = psycopg2.connect(
            host=params.host,
            port=params.port,
            database=params.database,
            user=params.username,
            password=params.password,
            connect_timeout=10
        )
        with conn.cursor() as cursor:
            cursor.execute(query, {"schema": params.schema, "pattern": pattern})
            rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception:
        return []
    finally:
        if conn:
            conn.close()


def compute_next_suffix(base_name: str, existing_names: List[str]) -> str:
    """
    Dado base_name e lista de existing_names, retorna nome sem conflito.
    """
    if base_name not in existing_names:
        return base_name
    pattern = re.compile(rf"^{re.escape(base_name)}_(\d+)$")
    nums: List[int] = []
    for name in existing_names:
        m = pattern.match(name)
        if m:
            try:
                nums.append(int(m.group(1)))
            except ValueError:
                pass
    next_num = max(nums) + 1 if nums else 1
    return f"{base_name}_{next_num}"
