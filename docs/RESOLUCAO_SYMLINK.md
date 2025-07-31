# Resolução: Problema com Symlink no dev_tools.bat

## Problema Identificado

O script `dev_tools.bat` não estava funcionando corretamente para criar links simbólicos. Vários fatores contribuíram para isso:

1. **Privilégios de Administrador**: Links simbólicos no Windows requerem privilégios elevados
2. **Estrutura de Diretórios**: Havia subdiretórios vazios causando confusão
3. **Arquivo metadata.txt**: Não estava sendo copiado corretamente
4. **Estratégia de Fallback**: Não havia uma estratégia robusta de fallback

## Soluções Implementadas

### 1. Limpeza da Estrutura

Removidos diretórios vazios que estavam causando confusão:
- `containers/`
- `controllers/`
- `models/`
- `services/`
- `utils/`

Agora a estrutura é plana e simples:
```
src/geoifsc/
├── __init__.py
├── geoifsc_plugin.py
├── raster_upload_dialog.py
├── raster_upload_controller.py
├── raster_uploader_service.py
├── raster_upload_params.py
├── connection_utils.py
├── icon.png.placeholder
└── metadata.txt (copiado durante instalação)
```

### 2. Estratégia Dupla de Instalação

O script agora usa uma estratégia dupla:

1. **Primeira tentativa**: Link simbólico via `mklink /D`
   - Ideal para desenvolvimento (alterações refletidas em tempo real)
   - Requer privilégios de administrador

2. **Fallback automático**: Cópia via `xcopy`
   - Funciona sem privilégios especiais
   - Requer atualização manual após mudanças

### 3. Scripts Adicionais Criados

#### `install_simple.bat`
Script simplificado que foca apenas na instalação:
- Mais direto e fácil de debugar
- Estratégia dupla (symlink -> cópia)
- Feedback claro sobre o tipo de instalação

#### `install_plugin.ps1`
Script PowerShell com verificações avançadas:
- Detecta se está rodando como administrador
- Validações completas de caminhos
- Feedback detalhado

### 4. Melhorias no dev_tools.bat

- **Cópia garantida do metadata.txt**: Sempre copia o arquivo, independentemente do método
- **Feedback melhorado**: Indica claramente se foi usado symlink ou cópia
- **Estratégia robusta**: Fallback automático sem erro fatal
- **Instruções claras**: Explica as diferenças entre os métodos

## Como Usar Agora

### Opção 1: dev_tools.bat (Completo)
```batch
# Execute como administrador para symlink, ou normal para cópia
dev_tools.bat
# Escolha opção 1 - Instalar plugin
```

### Opção 2: install_simple.bat (Simples)
```batch
# Script focado apenas em instalação
install_simple.bat
```

### Opção 3: install_plugin.ps1 (PowerShell)
```powershell
# Execute como administrador
.\install_plugin.ps1 -Force
```

## Resultados dos Testes

✅ **Plugin instalado com sucesso**
- Localização: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\GeoIFSC`
- Todos os arquivos presentes, incluindo `metadata.txt`
- Estrutura plana e compatível com QGIS

✅ **Fallback funcionando**
- Quando symlink falha, usa cópia automaticamente
- Usuário é informado sobre o método usado
- Instruções específicas para cada método

## Próximos Passos

1. **Testar no QGIS**: Abrir QGIS e ativar o plugin
2. **Validar funcionalidades**: Testar upload de raster
3. **Documentar workflow**: Atualizar documentação com nova estratégia

## Arquivos Modificados

- ✅ `dev_tools.bat` - Corrigido com estratégia dupla
- ✅ `src/geoifsc/` - Estrutura limpa e plana
- ✅ `install_simple.bat` - Novo script simples
- ✅ `install_plugin.ps1` - Novo script PowerShell
- ✅ Esta documentação

O problema foi completamente resolvido e agora temos múltiplas opções robustas para instalação do plugin.
