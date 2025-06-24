#!/bin/bash

# Script de Verificação de Cobertura Contínua para MedAI
# Este script executa verificações de cobertura em intervalos regulares

set -e

# Configurações
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/logs/coverage_monitor.log"
ALERT_THRESHOLD=75  # Alerta se cobertura cair abaixo de 75%
CRITICAL_THRESHOLD=60  # Crítico se cobertura cair abaixo de 60%

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Função para enviar alertas (placeholder - implementar integração real)
send_alert() {
    local level="$1"
    local message="$2"
    
    log "ALERT [$level]: $message"
    
    # Aqui você pode integrar com:
    # - Slack webhook
    # - Email
    # - Teams
    # - Discord
    # - Sistema de monitoramento
    
    # Exemplo de integração com Slack:
    # curl -X POST -H 'Content-type: application/json' \
    #   --data "{\"text\":\"🚨 MedAI Coverage Alert [$level]: $message\"}" \
    #   "$SLACK_WEBHOOK_URL"
}

# Função para verificar se serviços estão rodando
check_services() {
    log "Verificando serviços necessários..."
    
    # Verificar PostgreSQL
    if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
        log "⚠️  PostgreSQL não está disponível"
        return 1
    fi
    
    # Verificar Redis
    if ! redis-cli ping >/dev/null 2>&1; then
        log "⚠️  Redis não está disponível"
        return 1
    fi
    
    log "✅ Todos os serviços estão disponíveis"
    return 0
}

# Função para executar testes do backend
run_backend_tests() {
    log "🔍 Executando testes do backend..."
    
    cd "$PROJECT_ROOT/backend"
    
    # Configurar ambiente
    export PYTHONPATH="$PROJECT_ROOT/backend"
    export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/medai_test"
    export REDIS_URL="redis://localhost:6379"
    export TESTING=true
    
    # Executar testes com cobertura
    python3.11 -m pytest \
        --cov=app \
        --cov-report=json:coverage.json \
        --cov-report=html:htmlcov \
        --cov-report=term-missing \
        --cov-fail-under=80 \
        --quiet \
        tests/ || return 1
    
    log "✅ Testes do backend concluídos"
    return 0
}

# Função para executar testes do frontend
run_frontend_tests() {
    log "🔍 Executando testes do frontend..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Verificar se node_modules existe
    if [ ! -d "node_modules" ]; then
        log "📦 Instalando dependências do frontend..."
        npm ci
    fi
    
    # Executar testes com cobertura
    npm run test:coverage -- --run || return 1
    
    log "✅ Testes do frontend concluídos"
    return 0
}

# Função para analisar resultados de cobertura
analyze_coverage() {
    log "📊 Analisando resultados de cobertura..."
    
    cd "$PROJECT_ROOT"
    
    # Executar monitor de cobertura
    python3.11 scripts/coverage_monitor.py --project-root . > coverage_analysis.txt 2>&1
    local exit_code=$?
    
    # Ler resultados
    local coverage_summary=$(cat coverage_analysis.txt)
    log "Resumo da cobertura:\n$coverage_summary"
    
    # Extrair cobertura global (simplificado - melhorar parsing)
    local global_coverage=$(echo "$coverage_summary" | grep -o "Cobertura Global: [0-9.]*%" | grep -o "[0-9.]*" | head -1)
    
    if [ -n "$global_coverage" ]; then
        local coverage_int=$(echo "$global_coverage" | cut -d. -f1)
        
        if [ "$coverage_int" -lt "$CRITICAL_THRESHOLD" ]; then
            send_alert "CRITICAL" "Cobertura global caiu para $global_coverage% (abaixo de $CRITICAL_THRESHOLD%)"
        elif [ "$coverage_int" -lt "$ALERT_THRESHOLD" ]; then
            send_alert "WARNING" "Cobertura global está em $global_coverage% (abaixo de $ALERT_THRESHOLD%)"
        else
            log "✅ Cobertura global está adequada: $global_coverage%"
        fi
    fi
    
    return $exit_code
}

# Função para gerar relatório de tendências
generate_trend_report() {
    log "📈 Gerando relatório de tendências..."
    
    local reports_dir="$PROJECT_ROOT/coverage_reports"
    local trend_file="$reports_dir/coverage_trends.csv"
    
    # Criar arquivo de tendências se não existir
    if [ ! -f "$trend_file" ]; then
        echo "timestamp,global_coverage,backend_coverage,frontend_coverage,critical_coverage" > "$trend_file"
    fi
    
    # Extrair dados do último relatório
    local latest_report="$reports_dir/coverage_report_latest.json"
    if [ -f "$latest_report" ]; then
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        local global_cov=$(jq -r '.summary.global_coverage // 0' "$latest_report")
        local backend_cov=$(jq -r '.backend.total_coverage // 0' "$latest_report")
        local frontend_cov=$(jq -r '.frontend.total_coverage // 0' "$latest_report")
        local critical_cov=$(jq -r '.summary.critical_coverage // 0' "$latest_report")
        
        echo "$timestamp,$global_cov,$backend_cov,$frontend_cov,$critical_cov" >> "$trend_file"
        
        log "📊 Dados de tendência atualizados"
    fi
}

# Função para limpeza de arquivos antigos
cleanup_old_files() {
    log "🧹 Limpando arquivos antigos..."
    
    # Remover relatórios de cobertura com mais de 30 dias
    find "$PROJECT_ROOT/coverage_reports" -name "coverage_report_*.json" -mtime +30 -delete 2>/dev/null || true
    
    # Remover logs com mais de 7 dias
    find "$PROJECT_ROOT/logs" -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    log "✅ Limpeza concluída"
}

# Função principal
main() {
    local start_time=$(date +%s)
    
    echo -e "${BLUE}🚀 Iniciando monitoramento de cobertura MedAI${NC}"
    
    # Criar diretórios necessários
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/coverage_reports"
    
    log "=== Iniciando ciclo de monitoramento ==="
    
    # Verificar serviços
    if ! check_services; then
        log "❌ Serviços não disponíveis, abortando"
        exit 1
    fi
    
    # Executar testes
    local backend_success=true
    local frontend_success=true
    
    if ! run_backend_tests; then
        backend_success=false
        log "❌ Falha nos testes do backend"
    fi
    
    if ! run_frontend_tests; then
        frontend_success=false
        log "❌ Falha nos testes do frontend"
    fi
    
    # Analisar cobertura se pelo menos um conjunto de testes passou
    if [ "$backend_success" = true ] || [ "$frontend_success" = true ]; then
        if ! analyze_coverage; then
            log "⚠️  Análise de cobertura indicou problemas"
        fi
        
        generate_trend_report
    else
        send_alert "CRITICAL" "Todos os testes falharam - sistema pode estar com problemas graves"
    fi
    
    # Limpeza
    cleanup_old_files
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log "=== Ciclo de monitoramento concluído em ${duration}s ==="
    
    # Status final
    if [ "$backend_success" = true ] && [ "$frontend_success" = true ]; then
        echo -e "${GREEN}✅ Monitoramento concluído com sucesso${NC}"
        exit 0
    else
        echo -e "${RED}❌ Monitoramento concluído com falhas${NC}"
        exit 1
    fi
}

# Função para modo daemon
run_daemon() {
    local interval=${1:-3600}  # Default: 1 hora
    
    log "🔄 Iniciando modo daemon (intervalo: ${interval}s)"
    
    while true; do
        main
        log "😴 Aguardando próximo ciclo em ${interval}s..."
        sleep "$interval"
    done
}

# Função para mostrar ajuda
show_help() {
    cat << EOF
Script de Monitoramento de Cobertura MedAI

Uso: $0 [OPÇÃO]

OPÇÕES:
    -h, --help          Mostra esta ajuda
    -d, --daemon        Executa em modo daemon
    -i, --interval SEC  Intervalo em segundos para modo daemon (padrão: 3600)
    -c, --check-only    Apenas verifica cobertura sem executar testes
    -b, --backend-only  Executa apenas testes do backend
    -f, --frontend-only Executa apenas testes do frontend

EXEMPLOS:
    $0                          # Execução única
    $0 -d                       # Modo daemon (1 hora)
    $0 -d -i 1800              # Modo daemon (30 minutos)
    $0 -b                       # Apenas backend
    $0 -c                       # Apenas análise

EOF
}

# Parse de argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--daemon)
            DAEMON_MODE=true
            shift
            ;;
        -i|--interval)
            INTERVAL="$2"
            shift 2
            ;;
        -c|--check-only)
            CHECK_ONLY=true
            shift
            ;;
        -b|--backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        -f|--frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        *)
            echo "Opção desconhecida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Executar baseado nos argumentos
if [ "$DAEMON_MODE" = true ]; then
    run_daemon "${INTERVAL:-3600}"
elif [ "$CHECK_ONLY" = true ]; then
    analyze_coverage
elif [ "$BACKEND_ONLY" = true ]; then
    check_services && run_backend_tests && analyze_coverage
elif [ "$FRONTEND_ONLY" = true ]; then
    run_frontend_tests && analyze_coverage
else
    main
fi