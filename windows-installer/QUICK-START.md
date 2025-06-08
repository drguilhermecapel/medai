# SPEI Windows Installer - Quick Start Guide

## 🚀 **Construção Rápida do Instalador**

### **Pré-requisitos**
- ✅ Windows 10 ou superior (64-bit)
- ✅ Inno Setup 6 instalado: https://jrsoftware.org/isinfo.php
- ✅ Conexão com internet (para downloads)

### **Ordem OBRIGATÓRIA de Execução**

#### **1. PRIMEIRO - Preparar Componentes Runtime**
```cmd
cd caminho\para\medai\windows-installer
prepare-runtime.bat
```

**O que este script faz:**
- 📥 Baixa Python 3.11 embeddable (~50MB)
- 📥 Baixa Node.js runtime (~30MB)
- 📥 Baixa PostgreSQL portable (~200MB)
- 📥 Baixa Redis para Windows
- 📁 Cria estrutura completa do diretório `runtime/`

**⏳ AGUARDE todos os downloads terminarem!**

#### **2. DEPOIS - Construir Instalador**
```cmd
build-installer.bat
```

**O que este script faz:**
- ✅ Valida todos os componentes necessários
- ✅ Compila o instalador com Inno Setup
- ✅ Cria `dist/SPEI-Setup-v1.0.0.exe`

### **❌ Problemas Comuns**

| Problema | Causa | Solução |
|----------|-------|---------|
| `build-installer.bat` abre e fecha | Runtime não preparado | Execute `prepare-runtime.bat` primeiro |
| "Runtime components not found" | Diretório `runtime/` vazio | Execute `prepare-runtime.bat` e aguarde |
| "Inno Setup not found" | Inno Setup não instalado | Instale Inno Setup 6 |
| Downloads falham | Problemas de rede/proxy | Verifique conexão e execute novamente |

### **✅ Resultado Final**
- 📦 **Arquivo**: `dist/SPEI-Setup-v1.0.0.exe`
- 📏 **Tamanho**: ~200MB (com todos os componentes)
- 🎯 **Pronto**: Para distribuição aos profissionais de saúde

### **🔄 Ordem Correta Resumida**
```cmd
# 1. PRIMEIRO
prepare-runtime.bat

# 2. DEPOIS  
build-installer.bat
```

**Não execute `build-installer.bat` sem antes executar `prepare-runtime.bat`!**
