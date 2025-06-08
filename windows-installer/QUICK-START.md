# SPEI Windows Installer - Quick Start Guide

## 🚀 **Construção Simplificada do Instalador**

### **Pré-requisitos**
- ✅ Windows 10 ou superior (64-bit)
- ✅ Inno Setup 6 instalado: https://jrsoftware.org/isinfo.php
- ✅ Conexão com internet (para downloads automáticos)

### **🎯 INSTALADOR PORTÁTIL - UM ÚNICO PASSO**

#### **Construir Instalador Portátil (Tudo Automatizado)**
```cmd
cd caminho\para\medai\windows-installer
build-installer.bat
```

**O que este script faz:**
- ✅ Valida arquivos fonte da aplicação
- ✅ Compila o instalador portátil com Inno Setup
- ✅ Cria `dist/SPEI-Setup-v1.0.0.exe` (instalador portátil)
- 🎯 **PORTÁTIL**: Instalador baixa componentes automaticamente durante instalação
- 🚀 **DUPLO CLIQUE**: Funciona com apenas duplo clique, sem preparação manual

### **🔄 Durante a Instalação (Automático)**

O instalador criado irá automaticamente:
- 📥 Baixar Python 3.11 embeddable (~50MB)
- 📥 Baixar Node.js runtime (~30MB)
- 📥 Baixar PostgreSQL portable (~200MB)
- 📥 Baixar Redis para Windows (~5MB)
- 📥 Baixar Visual C++ Redistributables
- ⚙️ Configurar todos os componentes
- 🚀 Inicializar banco de dados
- 🏗️ Construir interface web
- ✅ Iniciar serviços

### **✨ Vantagens da Nova Abordagem**

| Antes | Agora |
|-------|-------|
| ❌ 2 passos manuais | ✅ 1 passo único |
| ❌ Downloads manuais | ✅ Downloads automáticos |
| ❌ Preparação complexa | ✅ Construção simples |
| ❌ ~200MB instalador | ✅ Instalador pequeno + downloads |
| ❌ Componentes pré-baixados | ✅ Sempre versões mais recentes |

### **❌ Problemas Comuns**

| Problema | Causa | Solução |
|----------|-------|---------|
| "Inno Setup not found" | Inno Setup não instalado | Instale Inno Setup 6 |
| "Backend source files not found" | Diretório incorreto | Execute de `windows-installer/` |
| "Frontend source files not found" | Arquivos fonte ausentes | Verifique estrutura do projeto |
| Downloads falham durante instalação | Problemas de rede/proxy | Usuário pode tentar novamente |

### **✅ Resultado Final - Instalador Portátil**
- 📦 **Arquivo**: `dist/SPEI-Setup-v1.0.0.exe` (instalador portátil)
- 📏 **Tamanho**: ~50MB (componentes baixados durante instalação)
- 🎯 **Portátil**: Funciona com duplo clique em qualquer Windows 10/11
- 🏥 **Profissional**: Para distribuição aos profissionais de saúde
- 🌐 **Inteligente**: Sempre baixa versões mais recentes dos componentes
- 🚀 **Zero Configuração**: Usuário final não precisa conhecimento técnico

### **🔄 Processo Ultra-Simplificado**
```cmd
# APENAS UM COMANDO PARA CRIAR INSTALADOR PORTÁTIL
build-installer.bat
```

**Agora é só executar um comando e distribuir o instalador portátil!**

### **📋 Para Desenvolvedores**

Se você ainda precisar preparar componentes manualmente para desenvolvimento:
```cmd
prepare-runtime.bat  # Ainda disponível para desenvolvimento
```

Mas para distribuição aos usuários finais, use apenas `build-installer.bat`.
