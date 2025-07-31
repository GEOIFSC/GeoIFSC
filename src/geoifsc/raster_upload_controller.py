"""
Controlador para upload de raster para PostGIS.
"""

from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal

from .raster_upload_params import ConnectionParams, RasterUploadParams
from .raster_uploader_service import RasterUploaderService
from .connection_utils import ConnectionUtils


class RasterUploadController(QObject):
    """Controlador para upload de raster."""
    
    connection_tested = pyqtSignal(bool, str)
    schemas_loaded = pyqtSignal(list)
    upload_progress = pyqtSignal(int)
    upload_started = pyqtSignal()
    upload_completed = pyqtSignal()
    file_processing_started = pyqtSignal(str)
    file_processing_success = pyqtSignal(str)
    file_processing_error = pyqtSignal(str, str)
    log_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._uploader_service = RasterUploaderService()
        self._current_connection: Optional[ConnectionParams] = None
        self._setup_connections()
    
    def _setup_connections(self):
        """Configura conexões de sinais do serviço."""
        self._uploader_service.progress_updated.connect(self.upload_progress.emit)
        self._uploader_service.file_upload_started.connect(self.file_processing_started.emit)
        self._uploader_service.file_upload_success.connect(self.file_processing_success.emit)
        self._uploader_service.file_upload_error.connect(self.file_processing_error.emit)
        self._uploader_service.upload_completed.connect(self.upload_completed.emit)
        self._uploader_service.log_message.connect(self.log_message.emit)
    
    def get_postgis_connections(self) -> List[tuple]:
        """Obtém conexões PostGIS do QGIS."""
        try:
            return ConnectionUtils.get_postgis_connections()
        except Exception as e:
            self.log_message.emit(f"Erro ao carregar conexões: {e}")
            return []
    
    def test_connection(self, connection: ConnectionParams):
        """Testa conexão com PostgreSQL."""
        try:
            self.log_message.emit("Testando conexão com os parâmetros fornecidos...")
            success, message = ConnectionUtils.test_connection(connection)

            if success:
                self.log_message.emit("Conexão bem-sucedida. Verificando extensão PostGIS...")
                has_postgis = ConnectionUtils.check_postgis_extension(connection)
                if not has_postgis:
                    success = False
                    message = "PostGIS não está habilitado neste banco"
                else:
                    self._current_connection = connection

            self.connection_tested.emit(success, message)
            self.log_message.emit(f"Resultado do teste de conexão: {message}")

        except Exception as e:
            error_msg = f"Erro no teste de conexão: {e}"
            self.connection_tested.emit(False, error_msg)
            self.log_message.emit(error_msg)
    
    def load_schemas(self, connection: ConnectionParams):
        """Carrega esquemas do banco de dados."""
        try:
            self.log_message.emit("Carregando esquemas...")
            schemas = ConnectionUtils.get_schemas(connection)
            self.schemas_loaded.emit(schemas)
            self.log_message.emit(f"Carregados {len(schemas)} esquemas")
            
        except Exception as e:
            error_msg = f"Erro ao carregar esquemas: {e}"
            self.log_message.emit(error_msg)
            self.schemas_loaded.emit(["public"])  # Fallback
    
    def start_upload(self, params: RasterUploadParams):
        """Inicia upload de rasters."""
        try:
            # Verifica conexão antes do upload
            success, message = ConnectionUtils.test_connection(params.connection)
            if not success:
                self.log_message.emit(f"Erro de conexão: {message}")
                return
            
            self.upload_started.emit()
            self._uploader_service.upload_rasters(params)
            
        except Exception as e:
            error_msg = f"Erro ao iniciar upload: {e}"
            self.log_message.emit(error_msg)
    
    def cancel_upload(self):
        """Cancela upload em andamento."""
        self._uploader_service.cancel_upload()
