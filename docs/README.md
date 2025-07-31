# 🗺️ Plugin GeoIFSC para QGIS

Plugin desenvolvido pelo **Instituto Federal de Santa Catarina (IFSC)** que oferece funcionalidades para upload de dados raster para **PostgreSQL/PostGIS**.

## 🎯 **Funcionalidades Principais**

### 📤 **Enviar Raster → PostGIS**
- **Upload múltiplo** de arquivos raster para PostgreSQL/PostGIS
- **Suporte a formatos**: TIFF, JPEG, PNG, GIF, BMP
- **Integração nativa** com conexões PostGIS já configuradas no QGIS
- **Conexão manual** para novos bancos de dados
- **Configurações avançadas**: SRID customizável, esquemas, sobrescrita, indexação, compressão
- **Interface moderna**: Painel de ajuda lateral, logs detalhados e progress bar
- **Processamento em lote**: Cada raster vira uma tabela separada automaticamente
- **Progresso visual**: Acompanhamento em tempo real com logs timestamps

## 🚀 **Instalação Rápida**

### **Pré-requisitos**
1. **QGIS 3.0+** instalado e funcionando
2. **PostgreSQL** com extensão **PostGIS** ativa
3. **Ferramentas PostgreSQL** (`raster2pgsql` e `psql`) no PATH ou em:
   - `C:\Program Files\PostgreSQL\[versão]\bin\`
   - `C:\Program Files (x86)\PostgreSQL\[versão]\bin\`

### **Instalar Plugin**
1. **Baixe** ou clone este repositório
2. **Execute** o script de instalação:
   ```batch
   # Windows
   .\install_plugin.ps1
   
   # Ou manual:
   .\dev_tools.bat
   # → Menu 1: Desenvolvimento & Instalação
   # → Opção 1: Instalar plugin no QGIS
   ```
3. **Reinicie o QGIS**
4. **Ative** o plugin em: `Plugins → Gerenciar e instalar plugins → Instalados → GeoIFSC`

## 📖 **Guia de Uso**

### **1. Acesso ao Plugin**
```
Menu QGIS → GeoIFSC → Banco de dados → Enviar Raster → PostGIS
```

### **2. Workflow Básico**
1. **📂 Selecionar Rasters**: Clique em "Selecionar Rasters" e escolha os arquivos
2. **🔌 Configurar Conexão**: Use conexões QGIS existentes ou insira dados manualmente
3. **✅ Testar Conexão**: Clique em "Testar Conexão" para validar
4. **📊 Atualizar Esquemas**: Carregue esquemas disponíveis do banco
5. **⚙️ Configurar Upload**: Defina prefixo da tabela, SRID e opções
6. **🚀 Executar**: Clique em "Enviar Rasters" e acompanhe o progresso

### **3. Nomeação Automática**
```
Nome da Tabela = [prefixo_opcional] + nome_do_arquivo
```
**Exemplo:**
- Arquivo: `temperatura_2024.tif`
- Prefixo: `dados_`
- Resultado: → `dados_temperatura_2024`

## 🔧 **Desenvolvimento**

### **Estrutura MVC**
```
src/geoifsc/
├── 📄 geoifsc_plugin.py              # Plugin principal QGIS
├── 📄 raster_upload_dialog.py        # 🖼️ VIEW: Interface PyQt5
├── 📄 raster_upload_controller.py    # 🎮 CONTROLLER: Lógica de controle
├── 📄 raster_uploader_service.py     # ⚙️ SERVICE: Upload com raster2pgsql
├── 📄 raster_upload_params.py        # 📊 MODEL: Parâmetros e dados
├── 📄 connection_utils.py            # 🛠️ UTILS: Conexões PostgreSQL
└── 📄 metadata.txt                   # Metadados do plugin
```

### **Scripts de Desenvolvimento**
```batch
# Ferramenta principal
.\dev_tools.bat

# Menu 1: Desenvolvimento & Instalação
# Menu 2: Empacotamento & Versão  
# Menu 3: Manutenção & Qualidade
# Menu 4: Logs & Utilitários
```

## 📋 **Status do Projeto**

✅ **Implementação Completa:**
- Arquitetura MVC robusta
- Interface PyQt5 moderna e responsiva
- Upload via `raster2pgsql` + `psql`
- Integração total com QGIS
- Validação rigorosa de parâmetros
- Tratamento de erros abrangente
- Logs detalhados com timestamps
- Cancelamento de operações em andamento

✅ **Testado e Validado:**
- Instalação automática via scripts
- Compatibilidade QGIS 3.0+
- PostgreSQL 12-17 com PostGIS
- Windows 10/11 (PowerShell 5.1+)
- Upload de arquivos até 5GB

## 🎓 **Documentação Técnica**

- 📘 **[DESENVOLVIMENTO.md](DESENVOLVIMENTO.md)** - Guia técnico completo
- 📜 **[HISTORICO.md](HISTORICO.md)** - Histórico de mudanças e correções
- 🚧 **[MANUTENCAO.md](MANUTENCAO.md)** - Guia de manutenção e releases futuras

## 📦 **Downloads**

### **📥 Release Atual: v1.0.0**
- **[GeoIFSC-1.0.0-plugin.zip](../dist/GeoIFSC-1.0.0-plugin.zip)** - Plugin completo para QGIS

### **⚙️ Instalação Manual**
1. Baixe o arquivo `GeoIFSC-1.0.0-plugin.zip`
2. Extraia para: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
3. Reinicie o QGIS e ative o plugin

## 🆘 **Suporte e Contribuição**

**Problemas ou dúvidas?**
1. Consulte a [documentação técnica](DESENVOLVIMENTO.md)
2. Execute: `.\dev_tools.bat → Menu 4 → Verificar instalação`
3. Abra uma issue neste repositório

**Desenvolvido com ❤️ pelo time GeoIFSC**
- Serviço de upload com raster2pgsql
- Controlador com validação e sinais
- Interface PyQt5 completa e responsiva
- Container de conexão customizado
- Painel de ajuda lateral
- Sistema de logs com timestamp
- Detecção automática de ferramentas PostgreSQL
- Suporte a conexões QGIS existentes
- Configuração manual de conexão
- Teste de conexão e PostGIS
- Validação de parâmetros
- Processamento em thread separada
- Cancelamento de upload
- Barra de progresso
- Ambiente virtual configurado
- Script de teste funcional

🎯 **Testado e Funcionando:**
- ✓ Detecção de raster2pgsql e psql
- ✓ Criação de parâmetros de conexão
- ✓ Parâmetros de upload
- ✓ Estrutura de classes MVC
- ✓ Importação de módulos
- ✓ Ambiente virtual Python

## 📞 Suporte

- **Issues**: Para reportar problemas
- **Email**: geoifsc@ifsc.edu.br
- **Logs**: Use os logs detalhados na interface para debug

---

**Desenvolvido com ❤️ pelo time GeoIFSC**
