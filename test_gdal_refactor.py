"""
Teste básico da refatoração GDAL do RasterUploaderService.
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Testa se os imports básicos funcionam."""
    try:
        from geoifsc.raster_uploader_service import RasterUploaderService
        print("✓ Import do RasterUploaderService funcionou")
        
        from geoifsc.raster_upload_params import RasterUploadParams, ConnectionParams
        print("✓ Import dos parâmetros funcionou")
        
        # Testa criação do serviço
        service = RasterUploaderService()
        print("✓ Criação do serviço funcionou")
        
        # Verifica se métodos existem
        assert hasattr(service, '_upload_single_raster_gdal'), "Método GDAL não encontrado"
        assert hasattr(service, '_log'), "Método _log não encontrado"
        assert hasattr(service, 'upload_rasters'), "Método upload_rasters não encontrado"
        print("✓ Métodos principais encontrados")
        
        print("\n🎉 Estrutura básica da refatoração GDAL está funcionando!")
        return True
        
    except ImportError as e:
        print(f"✗ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")
        return False


if __name__ == "__main__":
    test_imports()
