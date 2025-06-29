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

# Função para enviar alertas
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
    python -m pytest \
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
    npm run test:coverage || return 1
    
    log "✅ Testes do frontend concluídos"
    return 0
}

# Função para analisar cobertura
analyze_coverage() {
    log "📊 Analisando cobertura..."
    
    cd "$PROJECT_ROOT"
    
    # Executar script Python de análise
    python scripts/coverage_monitor.py --project-root "$PROJECT_ROOT"
    
    # Capturar resultado
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log "✅ Cobertura dentro dos limites aceitáveis"
    else
        log "❌ Cobertura abaixo dos limites"
        
        # Ler cobertura atual do último relatório
        local latest_report="$PROJECT_ROOT/coverage_reports/coverage_report_latest.json"
        if [ -f "$latest_report" ]; then
            local global_coverage=$(jq -r '.summary.global_coverage' "$latest_report")
            
            if (( $(echo "$global_coverage < $CRITICAL_THRESHOLD" | bc -l) )); then
                send_alert "CRITICAL" "Cobertura global caiu para ${global_coverage}% (limite crítico: ${CRITICAL_THRESHOLD}%)"
            elif (( $(echo "$global_coverage < $ALERT_THRESHOLD" | bc -l) )); then
                send_alert "WARNING" "Cobertura global em ${global_coverage}% (limite de alerta: ${ALERT_THRESHOLD}%)"
            fi
        fi
    fi
    
    return $exit_code
}

# Função para gerar relatório HTML
generate_html_report() {
    log "📝 Gerando relatório HTML consolidado..."
    
    local reports_dir="$PROJECT_ROOT/coverage_reports"
    local html_file="$reports_dir/coverage_dashboard.html"
    
    cat > "$html_file" << 'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedAI - Dashboard de Cobertura</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .metric-card {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .metric-value {
            font-size: 48px;
            font-weight: bold;
            margin: 10px 0;
        }
        .success { color: #28a745; }
        .warning { color: #ffc107; }
        .danger { color: #dc3545; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            transition: width 0.3s ease;
        }
        .timestamp {
            color: #6c757d;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 MedAI - Dashboard de Cobertura de Testes</h1>
            <p class="timestamp">Última atualização: <span id="timestamp"></span></p>
        </div>
        
        <div class="grid">
            <div class="metric-card">
                <h3>Cobertura Global</h3>
                <div class="metric-value" id="global-coverage">--</div>
                <div class="progress-bar">
                    <div class="progress-fill success" id="global-progress"></div>
                </div>
                <p>Meta: 80%</p>
            </div>
            
            <div class="metric-card">
                <h3>Componentes Críticos</h3>
                <div class="metric-value" id="critical-coverage">--</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="critical-progress"></div>
                </div>
                <p>Meta: 100%</p>
            </div>
            
            <div class="metric-card">
                <h3>Backend</h3>
                <div class="metric-value" id="backend-coverage">--</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="backend-progress"></div>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>Frontend</h3>
                <div class="metric-value" id="frontend-coverage">--</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="frontend-progress"></div>
                </div>
            </div>
        </div>
        
        <div class="metric-card">
            <h3>Componentes Críticos - Detalhes</h3>
            <ul id="critical-components"></ul>
        </div>
        
        <div class="metric-card">
            <h3>Recomendações</h3>
            <ul id="recommendations"></ul>
        </div>
    </div>
    
    <script>
        // Carrega dados do relatório mais recente
        fetch('coverage_report_latest.json')
            .then(response => response.json())
            .then(data => {
                // Atualiza timestamp
                document.getElementById('timestamp').textContent = new Date(data.timestamp).toLocaleString('pt-BR');
                
                // Atualiza métricas
                const globalCov = data.summary.global_coverage.toFixed(1);
                const criticalCov = data.summary.critical_coverage.toFixed(1);
                const backendCov = data.backend.total_coverage.toFixed(1);
                const frontendCov = data.frontend.total_coverage.toFixed(1);
                
                document.getElementById('global-coverage').textContent = globalCov + '%';
                document.getElementById('critical-coverage').textContent = criticalCov + '%';
                document.getElementById('backend-coverage').textContent = backendCov + '%';
                document.getElementById('frontend-coverage').textContent = frontendCov + '%';
                
                // Atualiza barras de progresso
                document.getElementById('global-progress').style.width = globalCov + '%';
                document.getElementById('critical-progress').style.width = criticalCov + '%';
                document.getElementById('backend-progress').style.width = backendCov + '%';
                document.getElementById('frontend-progress').style.width = frontendCov + '%';
                
                // Cores das barras
                updateProgressColor('global-progress', globalCov, 80);
                updateProgressColor('critical-progress', criticalCov, 100);
                updateProgressColor('backend-progress', backendCov, 80);
                updateProgressColor('frontend-progress', frontendCov, 80);
                
                // Componentes críticos
                const criticalList = document.getElementById('critical-components');
                Object.entries(data.backend.critical_components.components).forEach(([comp, cov]) => {
                    const li = document.createElement('li');
                    const icon = cov === 100 ? '✅' : '❌';
                    li.innerHTML = `${icon} ${comp}: <strong>${cov.toFixed(1)}%</strong>`;
                    criticalList.appendChild(li);
                });
                
                // Recomendações
                const recList = document.getElementById('recommendations');
                data.recommendations.forEach(rec => {
                    const li = document.createElement('li');
                    li.innerHTML = `<strong>[${rec.type.toUpperCase()}]</strong> ${rec.message}<br>→ ${rec.action}`;
                    recList.appendChild(li);
                });
            })
            .catch(error => console.error('Erro ao carregar dados:', error));
        
        function updateProgressColor(elementId, value, threshold) {
            const element = document.getElementById(elementId);
            element.classList.remove('success', 'warning', 'danger');
            
            if (value >= threshold) {
                element.classList.add('success');
            } else if (value >= threshold * 0.9) {
                element.classList.add('warning');
            } else {
                element.classList.add('danger');
            }
        }
    </script>
</body>
</html>
EOF
    
    # Criar link simbólico para o relatório mais recente
    local latest_json="$reports_dir/coverage_report_latest.json"
    if [ -f "$latest_json" ]; then
        log "✅ Dashboard HTML gerado: $html_file"
    fi
}

# Função principal de monitoramento
monitor_loop() {
    local interval=${1:-3600}  # Intervalo padrão: 1 hora
    
    log "🔄 Iniciando monitoramento contínuo (intervalo: ${interval}s)"
    
    while true; do
        log "=== Iniciando ciclo de verificação ==="
        
        # Verificar serviços
        if check_services; then
            # Executar testes
            local backend_ok=true
            local frontend_ok=true
            
            if ! run_backend_tests; then
                backend_ok=false
                send_alert "ERROR" "Falha ao executar testes do backend"
            fi
            
            if ! run_frontend_tests; then
                frontend_ok=false
                send_alert "ERROR" "Falha ao executar testes do frontend"
            fi
            
            # Analisar cobertura se pelo menos um conjunto passou
            if [ "$backend_ok" = true ] || [ "$frontend_ok" = true ]; then
                analyze_coverage
                generate_html_report
                
                # Criar link para último relatório
                cd "$PROJECT_ROOT/coverage_reports"
                latest_report=$(ls -t coverage_report_*.json | head -1)
                if [ -n "$latest_report" ]; then
                    ln -sf "$latest_report" coverage_report_latest.json
                fi
            fi
        else
            send_alert "ERROR" "Serviços necessários não estão disponíveis"
        fi
        
        log "=== Ciclo concluído. Próxima verificação em ${interval}s ==="
        sleep "$interval"
    done
}

# Parse argumentos
INTERVAL=3600
DAEMON=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--interval)
            INTERVAL="$2"
            shift 2
            ;;
        -d|--daemon)
            DAEMON=true
            shift
            ;;
        -h|--help)
            echo "Uso: $0 [opções]"
            echo "Opções:"
            echo "  -i, --interval <segundos>  Intervalo entre verificações (padrão: 3600)"
            echo "  -d, --daemon              Executar como daemon"
            echo "  -h, --help                Exibir esta ajuda"
            exit 0
            ;;
        *)
            echo "Opção desconhecida: $1"
            exit 1
            ;;
    esac
done

# Criar diretórios necessários
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/coverage_reports"

# Executar
if [ "$DAEMON" = true ]; then
    # Executar em background
    nohup "$0" --interval "$INTERVAL" > "$LOG_FILE" 2>&1 &
    PID=$!
    echo "🚀 Monitor iniciado em background (PID: $PID)"
    echo "$PID" > "$PROJECT_ROOT/coverage_monitor.pid"
else
    # Executar em foreground
    monitor_loop "$INTERVAL"
fi