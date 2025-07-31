"""
Modelos de dados para upload de raster.

Este módulo define as classes de dados usadas no sistema de upload.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ConnectionParams:
    """Parâmetros de conexão com PostgreSQL."""
    host: str
    port: int
    database: str
    username: str
    password: str
    schema: str = "public"


@dataclass
class RasterUploadParams:
    """Parâmetros para upload de raster."""
    raster_files: List[str]
    connection: ConnectionParams
    table_name_prefix: str = ""
    srid: int = 4326
    overwrite: bool = False
    use_index: bool = True
    use_compression: bool = True
    raster2pgsql_path: Optional[str] = None
    psql_path: Optional[str] = None
    cancel_check_func: Optional[callable] = None  # Adicionado cancel_check_func


@dataclass
class UploadProgress:
    """Informações de progresso do upload."""
    current_file: str
    files_completed: int
    total_files: int
    percentage: int
