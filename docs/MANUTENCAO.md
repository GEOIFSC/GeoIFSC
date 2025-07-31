# 🚧 **Guia de Manutenção Futura - Plugin GeoIFSC**

## 🎯 **Diretrizes para Desenvolvimento Contínuo**

Este documento estabelece as práticas recomendadas para manutenção e evolução do Plugin GeoIFSC.

---

## 📋 **Checklist de Lançamento**

### **✅ Antes de Cada Release**
```bash
# 1. Teste local completo
.\dev_tools.bat → Menu 1 → Opção 1: Instalar plugin
# Teste manual no QGIS: Menu GeoIFSC → Banco de dados → Enviar Raster → PostGIS

# 2. Validação automática
.\dev_tools.bat → Menu 3 → Opção 1: Validar estrutura
.\dev_tools.bat → Menu 3 → Opção 3: Rodar testes automatizados

# 3. Atualização de versão
.\dev_tools.bat → Menu 2 → Opção 1: Atualizar versão

# 4. Backup da versão atual
.\dev_tools.bat → Menu 2 → Opção 2: Fazer backup

# 5. Geração do release
.\dev_tools.bat → Menu 2 → Opção 3: Criar release empacotado

# 6. Verificação final
.\verify_installation.bat
```

### **📋 Testes Manuais Obrigatórios**
1. **Instalação limpa** do plugin
2. **Acesso ao menu** GeoIFSC no QGIS
3. **Abertura da interface** de upload
4. **Teste de conexão** com PostgreSQL/PostGIS
5. **Upload de raster** de teste (pequeno arquivo)
6. **Verificação no banco** se a tabela foi criada
7. **Cancelamento** de operação em andamento

---

## 🔧 **Estrutura de Arquivos a Manter**

### **📁 Arquivos Críticos (NÃO DELETAR)**
```
QGIS_GeoIFSC_Beta/
├── 📄 __init__.py                    # Entry point para alguns tipos de instalação
├── 📄 metadata.txt                   # Metadados do plugin QGIS (VERSÃO!)
├── 📄 requirements.txt               # Dependências Python
├── 📁 src/geoifsc/                   # 🚨 CÓDIGO FONTE PRINCIPAL
│   ├── 📄 __init__.py                # Factory function obrigatória
│   ├── 📄 geoifsc_plugin.py          # Plugin principal QGIS
│   ├── 📄 raster_upload_dialog.py    # Interface PyQt5
│   ├── 📄 raster_upload_controller.py # Controlador MVC  
│   ├── 📄 raster_uploader_service.py # Serviço de upload
│   ├── 📄 raster_upload_params.py    # Modelos de dados
│   ├── 📄 connection_utils.py        # Utilitários de conexão
│   └── 📄 metadata.txt               # Metadados para empacotamento
├── 📁 docs/                          # Documentação organizada
├── 📁 .venv/                         # Ambiente virtual para desenvolvimento
└── 📁 dist/                          # Releases empacotados
```

### **🛠️ Scripts de Desenvolvimento (Manter Atualizados)**
```
├── 📄 dev_tools.bat                  # 🚨 FERRAMENTA PRINCIPAL - manter atualizada
├── 📄 install_plugin.ps1             # Instalação PowerShell
├── 📄 install_simple.bat             # Instalação alternativa
├── 📄 package_simple.bat             # Empacotamento simples
├── 📄 verify_installation.bat        # Verificação de instalação
└── 📄 test_plugin.py                 # Testes standalone
```

---

## 📝 **Convenções de Versionamento**

### **Formato: `X.Y.Z`**
- **X** (Major): Mudanças que quebram compatibilidade
- **Y** (Minor): Novas funcionalidades sem quebrar compatibilidade  
- **Z** (Patch): Correções de bugs e melhorias menores

### **Exemplos**
```
1.0.0 → Release inicial
1.0.1 → Correção de bug menor
1.1.0 → Nova funcionalidade (ex: suporte a NetCDF)
2.0.0 → Mudança na arquitetura (ex: migração Qt6)
```

### **Atualização Automática**
```bash
# O script dev_tools.bat incrementa automaticamente:
.\dev_tools.bat → Menu 2 → Opção 1: Atualizar versão
# Incrementa Z (patch) por padrão
# Para minor/major, edite metadata.txt manualmente antes
```

---

## 🔄 **Fluxo de Desenvolvimento Recomendado**

### **1. 🌿 Branching Strategy**
```bash
main        # Branch de produção (releases estáveis)
├── dev     # Branch de desenvolvimento
└── feature/nova-funcionalidade  # Features específicas
```

### **2. 🔧 Workflow de Feature**
```bash
# 1. Criar branch
git checkout -b feature/suporte-netcdf

# 2. Desenvolvimento
# ... fazer alterações ...

# 3. Teste local completo
.\dev_tools.bat → Menu 3 → Opção 3: Rodar testes

# 4. Commit
git add .
git commit -m "feat: adiciona suporte a arquivos NetCDF"

# 5. Merge para dev
git checkout dev
git merge feature/suporte-netcdf

# 6. Teste final e merge para main
```

### **3. 📦 Release Process**
```bash
# 1. Merge dev → main
git checkout main
git merge dev

# 2. Atualizar versão
.\dev_tools.bat → Menu 2 → Opção 1: Atualizar versão

# 3. Criar release
.\dev_tools.bat → Menu 2 → Opção 3: Criar release empacotado

# 4. Git tag
git tag v1.1.0
git push origin v1.1.0

# 5. GitHub Release com dist/GeoIFSC-X.Y.Z-plugin.zip
```

---

## 🔮 **Roadmap de Melhorias Futuras**

### **🎯 Prioridade Alta (Próximos 6 meses)**
- [ ] **Suporte a mais formatos raster** (NetCDF, HDF5, COG)
- [ ] **Preview de dados** antes do upload (metadados, thumbnail)
- [ ] **Configurações avançadas** de raster2pgsql (chunk size, tiling)
- [ ] **Upload paralelo** para melhorar performance
- [ ] **Histórico de operações** com retry automático

### **🎯 Prioridade Média (6-12 meses)**
- [ ] **Suporte a outros SGBDs** (MySQL Spatial, SQLite/SpatiaLite)
- [ ] **Internacionalização** (i18n) - Inglês, Espanhol
- [ ] **Interface gráfica** para configuração avançada
- [ ] **Plugin para batch processing** via linha de comando
- [ ] **Integração com serviços cloud** (AWS RDS, Google Cloud SQL)

### **🎯 Prioridade Baixa (1+ anos)**
- [ ] **Migração para Qt6** (compatibilidade futura)
- [ ] **API REST** para upload via web
- [ ] **Dashboard de monitoramento** de uploads
- [ ] **Compressão inteligente** baseada no tipo de dados
- [ ] **Machine Learning** para otimização automática de parâmetros

---

## 🆘 **Solução de Problemas Comuns**

### **🐛 Plugin não aparece no QGIS**
```bash
# Diagnóstico
.\dev_tools.bat → Menu 4 → Opção 2: Verificar instalação QGIS

# Solução
.\dev_tools.bat → Menu 1 → Opção 1: Instalar plugin
# Se persistir: Menu 4 → Opção 4: Limpar cache do QGIS
```

### **🐛 Erro de Import**
```bash
# Verificar dependências
.\dev_tools.bat → Menu 3 → Opção 2: Verificar dependências

# Reinstalar ambiente
.\dev_tools.bat → Menu 1 → Opção 3: Criar ambiente virtual
.\dev_tools.bat → Menu 1 → Opção 4: Instalar dependências
```

### **🐛 raster2pgsql não encontrado**
```bash
# Verificar instalação PostgreSQL
where raster2pgsql
echo $env:PATH

# Solução: Instalar PostgreSQL com ferramentas completas
# Ou adicionar ao PATH manualmente
```

### **🐛 Falha no empacotamento**
```bash
# Validar estrutura primeiro
.\dev_tools.bat → Menu 3 → Opção 1: Validar estrutura

# Limpar arquivos temporários
.\dev_tools.bat → Menu 2 → Opção 4: Limpar arquivos temporários

# Tentar empacotamento novamente
.\dev_tools.bat → Menu 2 → Opção 3: Criar release empacotado
```

---

## 📞 **Contatos e Recursos**

### **🎓 Documentação Oficial**
- **README.md**: Guia do usuário principal
- **DESENVOLVIMENTO.md**: Documentação técnica completa
- **HISTORICO.md**: Histórico de mudanças e correções

### **🔧 Ferramentas de Desenvolvimento**
- **QGIS Plugin Builder**: Para estrutura inicial
- **Qt Designer**: Para design de interfaces PyQt5
- **PyQt5 Documentation**: Referência de componentes
- **PostgreSQL Docs**: Referência de raster2pgsql

### **📋 Checklist de Handover**
Quando transferir o projeto para outro desenvolvedor:

- [ ] Explicar estrutura MVC e padrões de código
- [ ] Demonstrar uso do `dev_tools.bat` completo
- [ ] Validar ambiente de desenvolvimento local
- [ ] Executar teste de release completo
- [ ] Documentar configurações específicas do ambiente
- [ ] Transferir acesso ao repositório GitHub
- [ ] Compartilhar credenciais de teste (PostgreSQL)

---

**🎯 Lembre-se: Sempre teste localmente antes de fazer release!**

**📧 Em caso de dúvidas, consulte a documentação técnica em `docs/DESENVOLVIMENTO.md`**
