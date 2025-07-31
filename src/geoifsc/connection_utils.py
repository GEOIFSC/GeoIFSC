"""
Utilitários para conexão com PostgreSQL/PostGIS.
"""

from typing import List, Tuple, Optional

try:
    from qgis.core import QgsSettings
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False

try:
    import psycopg2
    from psycopg2 import sql
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

from .raster_upload_params import ConnectionParams


class ConnectionUtils:
    """Utilitários para conexão PostgreSQL/PostGIS."""
    
    @staticmethod
    def test_connection(params: ConnectionParams) -> Tuple[bool, str]:
        """Testa conexão com PostgreSQL."""
        if not PSYCOPG2_AVAILABLE:
            return False, "Biblioteca psycopg2 não encontrada. Instale com: pip install psycopg2-binary"
        
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
                cursor.execute("SELECT 1;")
                cursor.fetchone()
                
            conn.close()
            return True, "Conectado"
            
        except psycopg2.OperationalError as e:
            return False, f"Erro de conexão: {str(e)}"
        except Exception as e:
            return False, f"Erro: {str(e)}"
    
    @staticmethod
    def get_schemas(params: ConnectionParams) -> List[str]:
        """Obtém lista de esquemas do banco de dados."""
        if not PSYCOPG2_AVAILABLE:
            return []
        
        try:
            conn = psycopg2.connect(
                host=params.host,
                port=params.port,
                database=params.database,
                user=params.username,
                password=params.password
            )
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    ORDER BY schema_name;
                """)
                schemas = [row[0] for row in cursor.fetchall()]
                
            conn.close()
            return schemas
            
        except Exception as e:
            return []
    
    @staticmethod
    def check_postgis_extension(params: ConnectionParams) -> bool:
        """Verifica se a extensão PostGIS está habilitada."""
        if not PSYCOPG2_AVAILABLE:
            return False
        
        try:
            conn = psycopg2.connect(
                host=params.host,
                port=params.port,
                database=params.database,
                user=params.username,
                password=params.password
            )
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM pg_extension 
                    WHERE extname = 'postgis';
                """)
                count = cursor.fetchone()[0]
                
            conn.close()
            return count > 0
            
        except Exception as e:
            return False
    
    @staticmethod
    def get_postgis_connections() -> List[Tuple[str, ConnectionParams]]:
        """Obtém conexões PostGIS do QGIS."""
        if not QGIS_AVAILABLE:
            return []
        
        try:
            settings = QgsSettings()
            connections = []
            
            settings.beginGroup("PostgreSQL/connections")
            connection_names = settings.childGroups()
            
            for name in connection_names:
                settings.beginGroup(name)
                
                params = ConnectionParams(
                    host=settings.value("host", "localhost"),
                    port=int(settings.value("port", 5432)),
                    database=settings.value("database", ""),
                    username=settings.value("username", ""),
                    password=settings.value("password", ""),
                    schema=settings.value("schema", "public")
                )
                
                connections.append((name, params))
                settings.endGroup()
            
            settings.endGroup()
            return connections
            
        except Exception as e:
            return []
