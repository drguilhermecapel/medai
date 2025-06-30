#!/bin/bash

# Script de Remoção Completa do ECG - MEDAI
# ATENÇÃO: Esta operação é IRREVERSÍVEL

echo "🚨 AVISO: Esta operação removerá PERMANENTEMENTE todas as funcionalidades ECG"
echo "Digite 'CONFIRMO' para continuar ou qualquer outra coisa para cancelar:"
read -r confirmation

if [ "$confirmation" != "CONFIRMO" ]; then
    echo "❌ Operação cancelada pelo usuário"
    exit 1
fi

echo "🔄 Iniciando remoção completa do ECG..."

# Criar diretório de backup para arquivos ECG
mkdir -p backup_ecg_$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backup_ecg_$(date +%Y%m%d_%H%M%S)"

echo "📁 Fazendo backup de arquivos ECG em $BACKUP_DIR..."

# Função para fazer backup antes de remover
backup_and_remove() {
    local file_path="$1"
    if [ -f "$file_path" ] || [ -d "$file_path" ]; then
        echo "🔄 Backup e remoção: $file_path"
        cp -r "$file_path" "$BACKUP_DIR/" 2>/dev/null
        rm -rf "$file_path"
    fi
}

# Remover arquivos ECG do backend
echo "🗑️ Removendo arquivos ECG do backend..."

# Services
backup_and_remove "backend/app/services/ecg_service.py"
backup_and_remove "backend/app/services/ecg_analysis_service.py"

# Models
find backend/app/models/ -name "*ecg*" -type f | while read -r file; do
    backup_and_remove "$file"
done

# Schemas
find backend/app/schemas/ -name "*ecg*" -type f | while read -r file; do
    backup_and_remove "$file"
done

# Repositories
find backend/app/repositories/ -name "*ecg*" -type f | while read -r file; do
    backup_and_remove "$file"
done

# API endpoints
find backend/app/api/ -name "*ecg*" -type f | while read -r file; do
    backup_and_remove "$file"
done

# Utils
find backend/app/utils/ -name "*ecg*" -type f | while read -r file; do
    backup_and_remove "$file"
done

# Tests
find backend/tests/ -name "*ecg*" -type f | while read -r file; do
    backup_and_remove "$file"
done

# Remover arquivos ECG do frontend
echo "🗑️ Removendo arquivos ECG do frontend..."

# Components
backup_and_remove "frontend/src/components/ECG/"
backup_and_remove "frontend/src/components/EcgAnalysis/"

# Services
backup_and_remove "frontend/src/services/ecgService.ts"
backup_and_remove "frontend/src/services/ecg_service.ts"

# Store/Redux
backup_and_remove "frontend/src/store/ecgSlice.ts"
backup_and_remove "frontend/src/store/ecg_slice.ts"

# Pages
backup_and_remove "frontend/src/pages/ECG/"
backup_and_remove "frontend/src/pages/EcgAnalysis/"

# Hooks
find frontend/src/hooks/ -name "*ecg*" -type f | while read -r file; do
    backup_and_remove "$file"
done

# Types
find frontend/src/types/ -name "*ecg*" -type f | while read -r file; do
    backup_and_remove "$file"
done

# Remover uploads e dados ECG
echo "🗑️ Removendo diretórios de dados ECG..."
backup_and_remove "backend/uploads/ecg/"
backup_and_remove "backend/data/ecg/"
backup_and_remove "backend/models/ecg/"

# Remover documentação ECG
echo "📚 Removendo documentação ECG..."
find docs/ -name "*ecg*" -type f 2>/dev/null | while read -r file; do
    backup_and_remove "$file"
done

# Remover migrações ECG específicas
echo "🗄️ Identificando migrações ECG..."
find backend/alembic/versions/ -name "*ecg*" -type f 2>/dev/null | while read -r file; do
    echo "⚠️ Migração ECG encontrada: $file (revisar manualmente)"
    backup_and_remove "$file"
done

echo "✅ Remoção de arquivos ECG concluída!"
echo "📁 Backup salvo em: $BACKUP_DIR"
echo "⚠️ Execute o script Python para limpeza precisa dos imports e referências"

