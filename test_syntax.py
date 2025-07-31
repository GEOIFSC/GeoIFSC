#!/usr/bin/env python3
"""
Script de teste para verificar sintaxe dos módulos refatorados.
"""

import ast
import sys

def check_syntax(filepath):
    """Verifica sintaxe de um arquivo Python."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Compila o AST para verificar sintaxe
        ast.parse(source, filename=filepath)
        print(f"✓ {filepath} - Sintaxe OK")
        return True
        
    except SyntaxError as e:
        print(f"✗ {filepath} - Erro de sintaxe: {e}")
        return False
    except Exception as e:
        print(f"✗ {filepath} - Erro: {e}")
        return False

def main():
    files_to_check = [
        r"src\geoifsc\raster_uploader_service.py",
        r"src\geoifsc\raster_upload_params.py",
        r"src\geoifsc\geoifsc_utils.py"
    ]
    
    all_ok = True
    for filepath in files_to_check:
        if not check_syntax(filepath):
            all_ok = False
    
    if all_ok:
        print("\n✓ Todos os arquivos passaram na verificação de sintaxe!")
    else:
        print("\n✗ Alguns arquivos têm problemas de sintaxe.")
        sys.exit(1)

if __name__ == "__main__":
    main()
