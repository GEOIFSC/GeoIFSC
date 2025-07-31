#!/usr/bin/env python3
"""
Teste funcional para verificar se os executáveis são encontrados corretamente.
"""

import os
import sys

# Adiciona o diretório src ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from geoifsc.geoifsc_utils import find_executable, get_postgres_possible_paths
    
    def test_find_executables():
        """Testa se os executáveis são encontrados na pasta bin/"""
        print("=== Teste de localização de executáveis ===")
        
        # Testa raster2pgsql
        possible_paths = get_postgres_possible_paths("raster2pgsql")
        raster2pgsql = find_executable("raster2pgsql", possible_paths)
        
        if raster2pgsql:
            print(f"✓ raster2pgsql encontrado: {raster2pgsql}")
            
            # Verifica se é do plugin
            plugin_bin = os.path.join(os.path.dirname(__file__), 'src', 'geoifsc', 'bin')
            if raster2pgsql.startswith(os.path.normpath(plugin_bin)):
                print("  └─ Usando executável do plugin ✓")
            else:
                print("  └─ Usando executável do sistema")
        else:
            print("✗ raster2pgsql não encontrado")
            
        # Testa psql
        possible_paths = get_postgres_possible_paths("psql")
        psql = find_executable("psql", possible_paths)
        
        if psql:
            print(f"✓ psql encontrado: {psql}")
            
            # Verifica se é do plugin
            plugin_bin = os.path.join(os.path.dirname(__file__), 'src', 'geoifsc', 'bin')
            if psql.startswith(os.path.normpath(plugin_bin)):
                print("  └─ Usando executável do plugin ✓")
            else:
                print("  └─ Usando executável do sistema")
        else:
            print("✗ psql não encontrado")
            
        return raster2pgsql is not None and psql is not None

    if __name__ == "__main__":
        success = test_find_executables()
        if success:
            print("\n✓ Teste de localização de executáveis: PASSOU")
        else:
            print("\n✗ Teste de localização de executáveis: FALHOU")
            sys.exit(1)
            
except Exception as e:
    print(f"Erro durante o teste: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
