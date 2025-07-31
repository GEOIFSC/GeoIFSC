# Otimização de Nomes de Tabela - Resumo

## Problema Original
- Loop de até 999 tentativas para encontrar nome único
- Uma query SQL para cada tentativa
- Ineficiente para casos com muitas tabelas similares

## Solução Implementada

### 1. fetch_existing_table_names()
- **Uma única query** para buscar todas as tabelas que começam com o prefixo
- Usa `LIKE` com padrão `base_name%`
- Retorna lista completa de nomes existentes
- **Tratamento robusto de erros**: Captura erros de psycopg2, ImportError e Exception genérica
- **Logs informativos**: Avisos específicos para facilitar diagnóstico

### 2. compute_next_suffix()
- Processa a lista localmente usando regex
- Extrai sufixos numéricos: `^base_name_(\d+)$`
- Calcula próximo sufixo livre matematicamente
- Sem necessidade de queries adicionais

### 3. _get_unique_table_name() Otimizado
```python
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
```

## Melhorias de Código

### Limpeza de Imports
- ✅ Removido import não usado `run_subprocess` de `raster_uploader_service.py`
- ✅ Mantido apenas `run_subprocess_with_cancel` que é efetivamente usado

### Tratamento de Erros Aprimorado
```python
except ImportError:
    # psycopg2 não está instalado
    print("AVISO: psycopg2 não encontrado. Não é possível verificar tabelas existentes.")
    return []
except psycopg2.Error as e:
    # Erro específico do PostgreSQL
    print(f"AVISO: Erro ao conectar ao PostgreSQL: {e}")
    return []
except Exception as e:
    # Outros erros
    print(f"AVISO: Não foi possível listar tabelas: {e}")
    return []
```

## Benefícios
- ✅ **Performance**: De O(n) queries para O(1) query
- ✅ **Escalabilidade**: Funciona eficientemente mesmo com centenas de tabelas
- ✅ **Confiabilidade**: Elimina limite artificial de 999 tentativas
- ✅ **Manutenibilidade**: Código mais limpo e testável
- ✅ **Robustez**: Tratamento específico para diferentes tipos de erro
- ✅ **Diagnóstico**: Logs informativos para troubleshooting

## Testes
- ✅ Função `compute_next_suffix` testada com 5 cenários diferentes
- ✅ Tratamento de erros testado com conexão inválida
- ✅ Todos os testes passando
