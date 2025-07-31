# 🔧 **Guia de Desenvolvimento - Plugin GeoIFSC**

## 🏗️ **Arquitetura do Projeto**

### **Padrão MVC Implementado**
O plugin segue rigorosamente o padrão **Model-View-Controller (MVC)** para manter o código organizado e manutenível:

```
src/geoifsc/
├── 📄 geoifsc_plugin.py              # 🎯 Entry Point (QGIS Plugin)
├── 📄 raster_upload_dialog.py        # 🖼️ VIEW: Interface PyQt5
├── 📄 raster_upload_controller.py    # 🎮 CONTROLLER: Lógica de controle
├── 📄 raster_uploader_service.py     # ⚙️ SERVICE: Business Logic
├── 📄 raster_upload_params.py        # 📊 MODEL: Data Classes
├── 📄 connection_utils.py            # 🛠️ UTILS: Database Connections
└── 📄 metadata.txt                   # Plugin metadata
```

### **📊 MODEL (Modelos de Dados)**
**Arquivo:** `raster_upload_params.py`
```python
@dataclass
class ConnectionParams:
    """Parâmetros de conexão PostgreSQL/PostGIS"""
    host: str
    port: int = 5432
    database: str
    username: str
    password: str
    schema: str = "public"

@dataclass  
class RasterUploadParams:
    """Parâmetros para upload de raster"""
    file_paths: List[str]
    connection: ConnectionParams
    table_prefix: str = ""
    srid: int = 4326
    overwrite: bool = False
    create_index: bool = True
    compress: bool = True
```

### **🖼️ VIEW (Interface PyQt5)**
**Arquivo:** `raster_upload_dialog.py`
- **Dialog Principal**: `QDialog` redimensionável (1200x800)
- **Layout Responsivo**: `QHBoxLayout` com painel lateral fixo
- **Componentes Principais**:
  - Seleção múltipla de arquivos raster
  - ConnectionContainer customizado
  - ComboBox de esquemas com validação rigorosa
  - QProgressBar para acompanhamento
  - QPlainTextEdit para logs com timestamp
  - Botões de ação com estados condicionais

### **🎮 CONTROLLER (Lógica de Controle)**
**Arquivo:** `raster_upload_controller.py`
- **Coordenação**: Conecta VIEW com SERVICES
- **Validação**: Valida parâmetros antes do upload
- **Gerenciamento de Estado**: Controla habilitação/desabilitação de botões
- **Tratamento de Sinais**: Conecta sinais PyQt5 entre componentes

### **⚙️ SERVICE (Lógica de Negócio)**
**Arquivo:** `raster_uploader_service.py`
- **Upload Core**: Execução de `raster2pgsql` + `psql`
- **Localização de Ferramentas**: Busca automática do raster2pgsql
- **Processamento em Lote**: Upload sequencial com tratamento de erros
- **Sinais PyQt5**: Emite progresso e resultados
- **Cancelamento**: Permite interromper operações

### **🛠️ UTILS (Utilitários)**
**Arquivo:** `connection_utils.py`
- **Teste de Conexão**: Validação com `psycopg2`
- **Integração QGIS**: Leitura de conexões PostGIS configuradas
- **Listagem de Esquemas**: Query SQL para carregar esquemas disponíveis

## 🔧 **Ferramentas de Desenvolvimento**

### **Script Principal: `dev_tools.bat`**
Ferramenta centralizada com interface de menus para automatizar tarefas:

#### **🚀 Menu 1: Desenvolvimento & Instalação**
```batch
1. Instalar plugin no QGIS        # Copia arquivos + reinicia QGIS
2. Testar plugin (sem QGIS)       # test_plugin.py standalone  
3. Criar ambiente virtual         # .venv com psycopg2
4. Instalar dependências          # pip install -r requirements.txt
```

#### **📦 Menu 2: Empacotamento & Versão**
```batch
1. Atualizar versão               # Incrementa metadata.txt
2. Fazer backup da versão atual   # ZIP com timestamp
3. Criar release empacotado       # GeoIFSC.zip para distribuição
4. Limpar arquivos temporários    # Cleanup de .pyc, __pycache__
```

#### **🧹 Menu 3: Manutenção & Qualidade**
```batch
1. Validar estrutura do plugin    # Verifica arquivos obrigatórios
2. Verificar dependências         # Lista módulos instalados
3. Rodar testes automatizados     # Suite de testes básicos
4. Gerar documentação             # Docstrings → Markdown
```

#### **📋 Menu 4: Logs & Utilitários**
```batch
1. Ver log de instalação          # Última execução detalhada
2. Verificar instalação QGIS      # Status do plugin no QGIS
3. Abrir pasta do plugin          # Explorer → diretório instalado
4. Limpar cache do QGIS           # Remove .pyc e reinicia
```

## 🎯 **Fluxo de Upload Técnico**

### **1. Localização de Ferramentas**
```python
def find_raster2pgsql() -> Optional[str]:
    """Busca raster2pgsql.exe nas localizações padrão"""
    # 1. Tenta shutil.which("raster2pgsql")
    # 2. C:\Program Files\PostgreSQL\[15-17]\bin\
    # 3. C:\Program Files (x86)\PostgreSQL\[15-17]\bin\
```

### **2. Construção do Comando**
```bash
# Comando completo gerado automaticamente:
raster2pgsql -s {SRID} -t auto -d/-a -I -C {arquivo.tif} {schema.table} | 
psql -h {HOST} -p {PORT} -U {USER} -d {DATABASE}
```

### **3. Flags Implementadas**
- **`-s SRID`**: Sistema de referência espacial
- **`-t auto`**: Tiling automático para performance
- **`-d`**: Drop table (sobrescrever) **OU** `-a` (append)
- **`-I`**: Criar índice espacial
- **`-C`**: Aplicar constraints
- **`-c`**: Compressão (opcional)

### **4. Execução com Subprocess**
```python
# Criação de processos sem janelas (Windows)
raster2pgsql_proc = subprocess.Popen(
    raster2pgsql_cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=env,
    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
)

psql_proc = subprocess.Popen(
    psql_cmd,
    stdin=raster2pgsql_proc.stdout,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=env,
    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
)
```

## 🧪 **Testes e Validação**

### **Teste Standalone: `test_plugin.py`**
```python
# Testa funcionalidades sem QGIS
python test_plugin.py

# Verifica:
# - Imports de todos os módulos
# - Criação de interfaces PyQt5
# - Localização de ferramentas PostgreSQL
# - Modelos de dados (dataclasses)
```

### **Teste de Instalação: `verify_installation.bat`**
```batch
# Verifica instalação completa no QGIS
# - Plugin ativo na lista
# - Menu GeoIFSC visível
# - Funcionalidade acessível
```

### **Teste de Estrutura:**
```python
# dev_tools.bat → Menu 3 → Opção 1
# Valida:
# - __init__.py presente
# - metadata.txt válido
# - Todos os módulos Python
# - Ícones e recursos
```

## 🔍 **Debugging e Logs**

### **Sistema de Logs Detalhados**
```python
# Logs com timestamp automático
def log_message(self, message: str):
    timestamp = QTime.currentTime().toString("hh:mm:ss")
    self.logs_area.appendPlainText(f"[{timestamp}] {message}")
```

### **Tratamento de Erros**
```python
# Captura erros de subprocess
if raster2pgsql_proc.returncode != 0:
    error_msg = raster2pgsql_proc.stderr.read().decode('utf-8', errors='ignore')
    self.upload_error.emit(file_path, f"raster2pgsql: {error_msg}")
    continue  # Continua com próximo arquivo
```

### **Debugging no QGIS**
```python
# Console Python do QGIS para debugging
import sys
sys.path.append(r"C:\path\to\your\plugin")
from src.geoifsc import test_plugin
test_plugin.run_tests()
```

## 📋 **Convenções de Código**

### **Estilo Python**
- **Docstrings**: Google Style para todas as funções
- **Type Hints**: Opcional mas recomendado
- **Nomeação**: snake_case para funções, PascalCase para classes
- **Imports**: Organizados por categorias (stdlib, terceiros, locais)

### **Estrutura de Arquivos**
```python
# Ordem padrão de imports
import os
import sys
from pathlib import Path
from typing import Optional, List

from PyQt5.QtWidgets import QDialog, QVBoxLayout
from qgis.core import QgsProject

from .raster_upload_params import ConnectionParams
```

### **Padrões de Commit**
```
feat: implementa nova funcionalidade
fix: corrige bug específico  
docs: atualiza documentação
test: adiciona ou modifica testes
refactor: refatora código sem mudar funcionalidade
```

## 🚀 **Workflow de Release**

### **1. Desenvolvimento**
```bash
# Trabalhe no branch dev
git checkout -b feature/nova-funcionalidade
# ... desenvolvimento ...
git commit -m "feat: adiciona funcionalidade X"
```

### **2. Teste Local**
```batch
# Teste completo
.\dev_tools.bat
# → Menu 1 → Opção 1: Instalar plugin
# → Menu 3 → Opção 3: Rodar testes
# → Teste manual no QGIS
```

### **3. Preparação de Release**
```batch
# Atualizar versão
.\dev_tools.bat
# → Menu 2 → Opção 1: Atualizar versão

# Criar backup
.\dev_tools.bat  
# → Menu 2 → Opção 2: Fazer backup

# Gerar release
.\dev_tools.bat
# → Menu 2 → Opção 3: Criar release empacotado
```

### **4. Distribuição**
- **Plugin Repository**: Upload via QGIS Plugin Repository
- **GitHub Releases**: Anexar `GeoIFSC.zip` como asset
- **Documentação**: Atualizar README.md e HISTORICO.md

## 🆘 **Solução de Problemas Comuns**

### **Plugin não aparece no QGIS**
```batch
# Verificar instalação
.\dev_tools.bat → Menu 4 → Opção 2

# Reinstalar
.\dev_tools.bat → Menu 1 → Opção 1
```

### **Erro "ModuleNotFoundError"**
```bash
# Instalar dependências
.\dev_tools.bat → Menu 1 → Opção 4

# Ou manual:
pip install -r requirements.txt
```

### **raster2pgsql não encontrado**
```bash
# Verificar PATH do PostgreSQL
echo $env:PATH  # PowerShell
echo %PATH%     # CMD

# Instalar PostgreSQL com ferramentas completas
```

### **Erro de conexão PostgreSQL**
```python
# Testar conexão manual
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="seu_db", 
    user="seu_user",
    password="sua_senha"
)
```

---

**💡 Dica**: Use sempre `dev_tools.bat` para operações de desenvolvimento - ele centraliza todas as tarefas e mantém logs detalhados!
