"""
Diálogo para upload de raster para PostGIS.

Este módulo implementa a interface gráfica para upload de rasters,
seguindo padrões PyQt5 e arquitetura MVC.
"""

import os
from pathlib import Path
from typing import List, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QPushButton, QLabel, QLineEdit, QSpinBox, QCheckBox, QComboBox,
    QListWidget, QPlainTextEdit, QProgressBar, QScrollArea,
    QWidget, QFileDialog, QSplitter, QFrame, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont
from qgis.core import Qgis
from qgis.utils import iface

nome_Botão = "Testar Conexão"

try:
    from qgis.gui import QgsProjectionSelectionWidget
    from qgis.core import QgsCoordinateReferenceSystem
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False

from .raster_upload_controller import RasterUploadController
from .raster_upload_params import ConnectionParams, RasterUploadParams


class ConnectionContainer(QGroupBox):
    """Container customizado para configuração de conexão."""
    
    log_emitted = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Conexão PostgreSQL/PostGIS", parent)
        self.controller: Optional[RasterUploadController] = None
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura interface do container de conexão."""
        layout = QVBoxLayout(self)
        
        # Conexões existentes
        existing_layout = QHBoxLayout()
        existing_layout.addWidget(QLabel("Conexões QGIS:"))
        
        self.connections_combo = QComboBox()
        self.connections_combo.setMinimumWidth(200)
        self.connections_combo.currentIndexChanged.connect(self._on_connection_selected)
        existing_layout.addWidget(self.connections_combo)
        
        existing_layout.addStretch()
        layout.addLayout(existing_layout)
        
        # Campos de conexão (sempre visíveis)
        fields_layout = QGridLayout()
        
        # Host
        fields_layout.addWidget(QLabel("Host:"), 0, 0)
        self.host_edit = QLineEdit("localhost")
        fields_layout.addWidget(self.host_edit, 0, 1)
        
        # Porta
        fields_layout.addWidget(QLabel("Porta:"), 0, 2)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(5432)
        fields_layout.addWidget(self.port_spin, 0, 3)
        
        # Database
        fields_layout.addWidget(QLabel("Database:"), 1, 0)
        self.database_edit = QLineEdit()
        fields_layout.addWidget(self.database_edit, 1, 1)
        
        # Usuário
        fields_layout.addWidget(QLabel("Usuário:"), 1, 2)
        self.username_edit = QLineEdit()
        fields_layout.addWidget(self.username_edit, 1, 3)
        
        # Senha
        fields_layout.addWidget(QLabel("Senha:"), 2, 0)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        fields_layout.addWidget(self.password_edit, 2, 1, 1, 3)
        
        layout.addLayout(fields_layout)
        
        # Teste de conexão
        test_layout = QHBoxLayout()
        self.test_btn = QPushButton(nome_Botão)
        self.test_btn.clicked.connect(self._test_connection)
        test_layout.addWidget(self.test_btn)
        
        self.connection_status = QLabel("Não testado")
        self.connection_status.setStyleSheet("color: gray;")
        test_layout.addWidget(self.connection_status)
        
        test_layout.addStretch()
        layout.addLayout(test_layout)
        
        # Esquema
        schema_layout = QHBoxLayout()
        schema_layout.addWidget(QLabel("Esquema:"))
        
        self.schema_combo = QComboBox()
        self.schema_combo.setEditable(True)
        self.schema_combo.addItem("-- Clique em 'Atualizar Esquemas' --")
        self.schema_combo.setCurrentIndex(0)
        schema_layout.addWidget(self.schema_combo)
        
        self.update_schemas_btn = QPushButton("Atualizar Esquemas")
        self.update_schemas_btn.clicked.connect(self._update_schemas)
        self.update_schemas_btn.setEnabled(False)
        schema_layout.addWidget(self.update_schemas_btn)
        
        # Conecta mudança de esquema para atualizar botão de upload
        self.schema_combo.currentIndexChanged.connect(self._update_upload_button_state)
        
        layout.addLayout(schema_layout)
    
    def set_controller(self, controller: RasterUploadController):
        """Define controlador para o container."""
        self.controller = controller
        self._load_existing_connections()
        
        # Conecta sinais do controlador
        self.controller.connection_tested.connect(self._on_connection_tested)
        self.controller.schemas_loaded.connect(self._on_schemas_loaded)
    
    def _load_existing_connections(self):
        """Carrega conexões existentes do QGIS."""
        if not self.controller:
            return
            
        connections = self.controller.get_postgis_connections()
        self.connections_combo.clear()
        self.connections_combo.addItem("-- Selecione uma conexão --", None)
        
        for name, params in connections:
            self.connections_combo.addItem(name, params)
    
    @pyqtSlot()
    def _on_connection_selected(self):
        """Preenche automaticamente os campos quando uma conexão é selecionada."""
        current_data = self.connections_combo.currentData()
        if current_data:
            # Preenche os campos com os dados da conexão selecionada
            self.host_edit.setText(current_data.host or "localhost")
            self.port_spin.setValue(current_data.port or 5432)
            self.database_edit.setText(current_data.database or "")
            self.username_edit.setText(current_data.username or "")
            self.password_edit.setText(current_data.password or "")
            
            # Reseta esquema para mostrar mensagem de atualizar
            self.schema_combo.clear()
            self.schema_combo.addItem("-- Clique em 'Atualizar Esquemas' --")
            self.schema_combo.setCurrentIndex(0)
        else:
            # Limpa os campos se "-- Selecione uma conexão --" for selecionado
            self.host_edit.setText("localhost")
            self.port_spin.setValue(5432)
            self.database_edit.setText("")
            self.username_edit.setText("")
            self.password_edit.setText("")
            
            # Reseta esquema
            self.schema_combo.clear()
            self.schema_combo.addItem("-- Clique em 'Atualizar Esquemas' --")
            self.schema_combo.setCurrentIndex(0)
    
    @pyqtSlot()
    def _test_connection(self):
        """Testa conexão sem janelas modais, apenas log e label de status."""
        self._log("Botão 'Teste de Conexão' clicado")
        
        if not self.controller:
            self._log("Erro: Controlador não definido.")
            self.connection_status.setText("Erro: sem controlador ✗")
            self.connection_status.setStyleSheet("color: red; font-weight: bold;")
            return

        params = self.get_connection_params_for_test()
        if not params:
            msg = "Host, Database e Usuário são obrigatórios para teste."
            self._log(f"Erro: {msg}")
            self.connection_status.setText("Parâmetros inválidos ✗")
            self.connection_status.setStyleSheet("color: red; font-weight: bold;")
            return

        self._log(f"Iniciando teste de conexão: {params}")
        self.connection_status.setText("Testando conexão...")
        self.connection_status.setStyleSheet("color: orange; font-weight: bold;")
        
        iface.messageBar().pushMessage(
            "GeoIFSC", "Iniciando teste de conexão...", level=Qgis.Info, duration=3
        )
        
        try:
            self.controller.test_connection(params)
        except Exception as e:
            import traceback
            error_msg = f"Erro inesperado no teste de conexão: {e}"
            self._log(error_msg)
            self._log(traceback.format_exc())
            self.connection_status.setText("Erro interno ✗")
            self.connection_status.setStyleSheet("color: red; font-weight: bold;")

    
    @pyqtSlot()
    def _update_schemas(self):
        """Atualiza lista de esquemas."""
        self._log("Botão 'Atualizar Esquemas' clicado")
        
        if not self.controller:
            self._log("Erro: Controlador não definido para atualizar esquemas")
            return

        # Usa parâmetros básicos (inclui 'public' como esquema default)
        params = self.get_connection_params_for_test()
        if params:
            self._log(f"Carregando esquemas para: {params.host}:{params.port}/{params.database}")
            self.controller.load_schemas(params)
        else:
            self._log("Erro: Parâmetros de conexão inválidos para carregar esquemas")
    
    @pyqtSlot(bool, str)
    def _on_connection_tested(self, success: bool, message: str):
        """Atualiza apenas o label e o log; sem pop-ups."""
        self._log(f"_on_connection_tested chamado: success={success}, message='{message}'")
        
        status_text = "Conectado ✓" if success else "Falha na conexão ✗"
        status_color = "green" if success else "red"
        self.connection_status.setText(status_text)
        self.connection_status.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        self._log(f"Resultado do teste: {'Sucesso' if success else 'Falha'} – {message}")
        
        # Ativa ou desativa o botão de atualizar esquemas
        self.update_schemas_btn.setEnabled(success)
        self._log(f"Botão 'Atualizar Esquemas' {'habilitado' if success else 'desabilitado'}")
        
        self._update_upload_button_state()
    
    def _update_upload_button_state(self):
        """Atualiza estado do botão de upload através do diálogo pai."""
        # Procura o diálogo pai e chama seu método de atualização
        parent = self.parent()
        while parent and not hasattr(parent, '_update_upload_button_state'):
            parent = parent.parent()
        if parent and hasattr(parent, '_update_upload_button_state'):
            parent._update_upload_button_state()
    
    @pyqtSlot(list)
    def _on_schemas_loaded(self, schemas: List[str]):
        """Callback para esquemas carregados."""
        self._log(f"Esquemas carregados: {schemas}")
        
        current_text = self.schema_combo.currentText()
        self.schema_combo.clear()
        
        # Adiciona esquemas carregados
        if schemas:
            self.schema_combo.addItems(schemas)
            self._log(f"Adicionados {len(schemas)} esquemas ao combo")
            
            # Se 'public' estiver na lista, seleciona por padrão
            if "public" in schemas:
                index = self.schema_combo.findText("public")
                self.schema_combo.setCurrentIndex(index)
                self._log("Esquema 'public' selecionado automaticamente")
            else:
                # Caso contrário, seleciona o primeiro
                self.schema_combo.setCurrentIndex(0)
                self._log(f"Primeiro esquema selecionado: {schemas[0] if schemas else 'N/A'}")
        else:
            # Se não houver esquemas, volta para a mensagem
            self.schema_combo.addItem("-- Clique em 'Atualizar Esquemas' --")
            self.schema_combo.setCurrentIndex(0)
            self._log("Nenhum esquema encontrado, voltando para mensagem padrão")
    
    def get_connection_params_for_test(self) -> Optional[ConnectionParams]:
        """Obtém parâmetros de conexão sem exigir esquema (para teste de conexão)."""
        # Verifica se campos obrigatórios estão preenchidos
        if not all([
            self.host_edit.text().strip(),
            self.database_edit.text().strip(),
            self.username_edit.text().strip()
        ]):
            return None
        
        # Para teste, usa 'public' como esquema padrão se não houver um válido
        schema_text = self.schema_combo.currentText()
        if schema_text.startswith("-- Clique em") or not schema_text.strip():
            schema_text = "public"  # Esquema padrão para teste
        
        return ConnectionParams(
            host=self.host_edit.text().strip(),
            port=self.port_spin.value(),
            database=self.database_edit.text().strip(),
            username=self.username_edit.text().strip(),
            password=self.password_edit.text(),
            schema=schema_text.strip()
        )
    
    def get_connection_params(self) -> Optional[ConnectionParams]:
        """Obtém parâmetros de conexão dos campos do formulário."""
        # Verifica se campos obrigatórios estão preenchidos
        if not all([
            self.host_edit.text().strip(),
            self.database_edit.text().strip(),
            self.username_edit.text().strip()
        ]):
            return None
        
        # Validação explícita do esquema selecionado
        schema_text = self.schema_combo.currentText()
        if schema_text.startswith("-- Clique em") or not schema_text.strip():
            # Retorna None se o usuário não selecionou um esquema válido
            return None
        
        return ConnectionParams(
            host=self.host_edit.text().strip(),
            port=self.port_spin.value(),
            database=self.database_edit.text().strip(),
            username=self.username_edit.text().strip(),
            password=self.password_edit.text(),
            schema=schema_text.strip()
        )
    
    def _log(self, message: str):
        """Emite mensagem de log via sinal."""
        print(f"[LOG] {message}")
        self.log_emitted.emit(message)


class HelpPanel(QFrame):
    """Painel lateral de ajuda com informações sobre o uso da ferramenta."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setMaximumWidth(300)
        self.setMinimumWidth(250)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura interface do painel de ajuda."""
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Ajuda - Enviar Raster")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border-radius: 4px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Scroll area para o conteúdo
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget de conteúdo
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Conteúdo de ajuda
        help_text = QLabel("""
<b>🔧 Como usar:</b><br><br>

<b>1. Selecionar Arquivos:</b><br>
• Clique em "Selecionar Rasters"<br>
• Formatos: TIFF, JPEG, PNG, etc.<br>
• Seleção múltipla permitida<br><br>

<b>2. Configurar Conexão:</b><br>
• Selecione uma conexão do QGIS<br>
• Os campos serão preenchidos automaticamente<br>
• Ou preencha manualmente<br>
• Teste a conexão antes de continuar<br><br>

<b>3. Configurações:</b><br>
• <b>Prefixo:</b> opcional, adicionado ao nome da tabela<br>
• <b>Sobrescrever:</b> substitui tabela se já existir<br>
• <b>CRS:</b> sistema de coordenadas do raster<br>
&nbsp;&nbsp;→ Padrão: SIRGAS 2000 / UTM 22S<br><br>

<b>4. Executar Upload:</b><br>
• Cada arquivo vira uma tabela no PostGIS<br>
• Nome da tabela = nome do arquivo<br>
• Acompanhe o progresso nos logs<br><br>

<b>⚙️ Requisitos Técnicos:</b><br>
• PostgreSQL com extensão PostGIS<br>
• Ferramentas raster2pgsql e psql<br>
• Conexão ativa com o banco<br><br>

<b>💡 Dicas:</b><br>
• Teste a conexão antes do upload<br>
• Use esquemas para organizar dados<br>
• Verifique o CRS dos seus rasters<br>
• Logs mostram detalhes do processo
        """)
        
        help_text.setWordWrap(True)
        help_text.setAlignment(Qt.AlignTop)
        help_text.setStyleSheet("""
            QLabel {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 12px;
                line-height: 1.4;
                font-size: 9pt;
            }
        """)
        
        content_layout.addWidget(help_text)
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)


class RasterUploadDialog(QDialog):
    """Diálogo principal para upload de raster."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Tornar diálogo não-modal para não bloquear o console Python do QGIS
        self.setModal(False)
        self.controller = RasterUploadController()
        self.selected_files: List[str] = []
        self._setup_ui()
        self._connect_signals()
        self.setWindowTitle("Enviar Raster → PostGIS")
        self.resize(1200, 800)
    
    def _setup_ui(self):
        """Configura interface principal com layout em duas colunas."""
        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        
        # Coluna esquerda: formulário
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        
        # Scroll area para o formulário
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Seções do formulário
        self._create_file_selection_section(content_layout)
        self._create_connection_section(content_layout)
        self._create_settings_section(content_layout)
        self._create_progress_section(content_layout)
        self._create_logs_section(content_layout)
        self._create_action_buttons(content_layout)
        
        scroll.setWidget(content_widget)
        left_layout.addWidget(scroll)
        
        # Coluna direita: painel de ajuda
        help_panel = HelpPanel()
        
        # Adiciona as colunas ao layout principal
        main_layout.addWidget(left_column, 3)  # 75% do espaço
        main_layout.addWidget(help_panel, 1)   # 25% do espaço
    
    def _create_file_selection_section(self, parent_layout):
        """Cria seção de seleção de arquivos."""
        group = QGroupBox("Seleção de Arquivos Raster")
        layout = QVBoxLayout(group)
        
        # Botão selecionar
        btn_layout = QHBoxLayout()
        self.select_files_btn = QPushButton("Selecionar Rasters")
        self.select_files_btn.clicked.connect(self._select_files)
        btn_layout.addWidget(self.select_files_btn)
        
        self.clear_selection_btn = QPushButton("Limpar Seleção")
        self.clear_selection_btn.clicked.connect(self._clear_selection)
        btn_layout.addWidget(self.clear_selection_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Lista de arquivos
        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(150)
        layout.addWidget(self.files_list)
        
        parent_layout.addWidget(group)
    
    def _create_connection_section(self, parent_layout):
        """Cria seção de conexão."""
        self.connection_container = ConnectionContainer()
        self.connection_container.set_controller(self.controller)
        # Conecta sinal de log do container ao método de log do diálogo
        self.connection_container.log_emitted.connect(self.append_log)
        parent_layout.addWidget(self.connection_container)
    
    def _create_settings_section(self, parent_layout):
        """Cria seção de configurações."""
        group = QGroupBox("Configurações de Upload")
        layout = QGridLayout(group)
        
        # Nome da tabela (prefixo)
        layout.addWidget(QLabel("Prefixo da Tabela:"), 0, 0)
        self.table_prefix_edit = QLineEdit()
        self.table_prefix_edit.setPlaceholderText("Deixe vazio para usar apenas o nome do arquivo")
        # Conecta mudança no prefixo para atualizar botão de upload
        self.table_prefix_edit.textChanged.connect(self._update_upload_button_state)
        layout.addWidget(self.table_prefix_edit, 0, 1, 1, 2)
        
        # Sobrescrever (logo abaixo do nome da tabela)
        self.overwrite_check = QCheckBox("Sobrescrever se existir")
        layout.addWidget(self.overwrite_check, 1, 0, 1, 3)
        
        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator, 2, 0, 1, 3)
        
        # CRS/SRID
        layout.addWidget(QLabel("Sistema de Coordenadas:"), 3, 0)
        
        if QGIS_AVAILABLE:
            # Usa o seletor de CRS do QGIS
            self.crs_selector = QgsProjectionSelectionWidget()
            # Cria objeto CRS para SIRGAS 2000 / UTM zona 22S
            crs = QgsCoordinateReferenceSystem("EPSG:31982")
            self.crs_selector.setCrs(crs)
            layout.addWidget(self.crs_selector, 3, 1, 1, 2)
        else:
            # Fallback para QSpinBox se QGIS não estiver disponível
            self.srid_spin = QSpinBox()
            self.srid_spin.setRange(1, 999999)
            self.srid_spin.setValue(31982)  # SIRGAS 2000 / UTM zona 22S
            layout.addWidget(self.srid_spin, 3, 1)
            
            # Label informativo
            info_label = QLabel("EPSG:31982 (SIRGAS 2000 / UTM 22S)")
            info_label.setStyleSheet("color: gray; font-style: italic;")
            layout.addWidget(info_label, 3, 2)
        
        parent_layout.addWidget(group)
    
    def _get_srid_value(self) -> int:
        """Obtém valor do SRID selecionado."""
        if QGIS_AVAILABLE and hasattr(self, 'crs_selector'):
            try:
                crs = self.crs_selector.crs()
                if crs.isValid():
                    # Tenta extrair o código EPSG do authid
                    authid = crs.authid()
                    if authid and ':' in authid:
                        epsg_code = authid.split(':')[1]
                        return int(epsg_code)
                    # Se não conseguir, tenta o postgisSrid()
                    elif hasattr(crs, 'postgisSrid') and crs.postgisSrid() > 0:
                        return crs.postgisSrid()
                # Fallback para SIRGAS 2000 / UTM 22S
                return 31982
            except (ValueError, AttributeError):
                return 31982
        else:
            return self.srid_spin.value()
    
    def _create_progress_section(self, parent_layout):
        """Cria seção de progresso."""
        group = QGroupBox("Progresso")
        layout = QVBoxLayout(group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        
        parent_layout.addWidget(group)
    
    def _create_logs_section(self, parent_layout):
        """Cria seção de logs."""
        group = QGroupBox("Logs")
        layout = QVBoxLayout(group)
        
        self.logs_text = QPlainTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setMaximumHeight(200)
        self.logs_text.setStyleSheet("""
            QPlainTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 9pt;
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)
        layout.addWidget(self.logs_text)
        
        parent_layout.addWidget(group)
    
    def _create_action_buttons(self, parent_layout):
        """Cria botões de ação."""
        layout = QHBoxLayout()
        
        self.upload_btn = QPushButton("Enviar Rasters")
        self.upload_btn.clicked.connect(self._start_upload)
        self.upload_btn.setEnabled(False)
        layout.addWidget(self.upload_btn)
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self._cancel_upload)
        self.cancel_btn.setVisible(False)
        layout.addWidget(self.cancel_btn)
        
        layout.addStretch()
        
        self.close_btn = QPushButton("Fechar")
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.close_btn)
        
        parent_layout.addLayout(layout)
    
    def _connect_signals(self):
        """Conecta sinais do controlador."""
        self.controller.upload_progress.connect(self._on_upload_progress)
        self.controller.upload_started.connect(self._on_upload_started)
        self.controller.upload_completed.connect(self._on_upload_completed)
        self.controller.file_processing_started.connect(self._on_file_started)
        self.controller.file_processing_success.connect(self._on_file_success)
        self.controller.file_processing_error.connect(self._on_file_error)
        self.controller.log_message.connect(self._on_log_message)
        self.controller.connection_tested.connect(self._on_connection_tested)
        
        # Conecta sinais para atualizar estado do botão "Enviar Rasters"
        self.controller.connection_tested.connect(lambda success, msg: self._update_upload_button_state())
        self.controller.schemas_loaded.connect(lambda schemas: self._update_upload_button_state())
    
    @pyqtSlot()
    def _select_files(self):
        """Seleciona arquivos raster."""
        file_filter = "Raster Files (*.tif *.tiff *.jpg *.jpeg *.png *.gif *.bmp);;All Files (*)"
        files, _ = QFileDialog.getOpenFileNames(
            self, "Selecionar Arquivos Raster", "", file_filter
        )
        
        if files:
            self.selected_files = files
            self._update_files_list()
            self._update_upload_button_state()
    
    @pyqtSlot()
    def _clear_selection(self):
        """Limpa seleção de arquivos."""
        self.selected_files.clear()
        self._update_files_list()
        self._update_upload_button_state()
    
    def _update_files_list(self):
        """Atualiza lista de arquivos selecionados."""
        self.files_list.clear()
        for file_path in self.selected_files:
            filename = Path(file_path).name
            self.files_list.addItem(f"{filename} ({file_path})")
    
    def _update_upload_button_state(self):
        """Atualiza estado do botão de upload."""
        has_files = bool(self.selected_files)
        connection = self.connection_container.get_connection_params()
        has_connection = connection is not None
        
        self.upload_btn.setEnabled(has_files and has_connection)
    
    @pyqtSlot()
    def _start_upload(self):
        """Inicia upload de rasters."""
        connection = self.connection_container.get_connection_params()
        if not connection:
            self._log("Erro: Parâmetros de conexão inválidos")
            return
        
        params = RasterUploadParams(
            raster_files=self.selected_files.copy(),
            connection=connection,
            table_name_prefix=self.table_prefix_edit.text().strip(),
            srid=self._get_srid_value(),
            overwrite=self.overwrite_check.isChecked()
        )
        
        self.controller.start_upload(params)
    
    @pyqtSlot()
    def _cancel_upload(self):
        """Cancela upload em andamento."""
        self.controller.cancel_upload()
    
    @pyqtSlot(int)
    def _on_upload_progress(self, progress: int):
        """Atualiza progresso do upload."""
        self.progress_bar.setValue(progress)
    
    @pyqtSlot()
    def _on_upload_started(self):
        """Callback para início do upload."""
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        self.upload_btn.setVisible(False)
        self.cancel_btn.setVisible(True)
        self._log("Upload iniciado...")
    
    @pyqtSlot()
    def _on_upload_completed(self):
        """Callback para conclusão do upload."""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.upload_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        self._log("Upload concluído.")
    
    @pyqtSlot(str)
    def _on_file_started(self, filename: str):
        """Callback para início do processamento de arquivo."""
        self.progress_label.setText(f"Processando: {Path(filename).name}")
    
    @pyqtSlot(str)
    def _on_file_success(self, filename: str):
        """Callback para sucesso no processamento de arquivo."""
        pass  # Log já é emitido pelo controlador
    
    @pyqtSlot(str, str)
    def _on_file_error(self, filename: str, error: str):
        """Callback para erro no processamento de arquivo."""
        pass  # Log já é emitido pelo controlador
    
    @pyqtSlot(str)
    def _on_log_message(self, message: str):
        """Adiciona mensagem ao log."""
        self._log(message)
    
    @pyqtSlot(bool, str)
    def _on_connection_tested(self, success: bool, message: str):
        """Callback para teste de conexão - apenas atualiza logs, sem janelas modais."""
        self._update_upload_button_state()
        # registra apenas no log, sem pop-ups
        if success:
            self._log("Conexão bem-sucedida.")
        else:
            self._log(f"Falha ao conectar: {message}")
    
    def _log(self, message: str):
        """Adiciona mensagem ao log."""
        self.logs_text.appendPlainText(message)
        # Rola para o final
        scrollbar = self.logs_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def append_log(self, message: str):
        """Método para receber logs via sinal do ConnectionContainer."""
        self._log(message)
