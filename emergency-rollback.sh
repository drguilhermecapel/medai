#!/bin/bash
# emergency-rollback.sh
# Emergency rollback script for MedAI security updates

echo "=== MEDAI EMERGENCY ROLLBACK INITIATED ==="
echo "Timestamp: $(date)"

# Function to log rollback actions
log_action() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a rollback.log
}

# Check if git tag exists for rollback point
if [ -z "$1" ]; then
    echo "Usage: $0 <commit-hash-or-tag>"
    echo "Available recent commits:"
    git log --oneline -10
    exit 1
fi

ROLLBACK_POINT=$1

log_action "Starting emergency rollback to: $ROLLBACK_POINT"

# 1. Stop current services
log_action "Stopping current services..."
if [ -f "docker-compose.yml" ]; then
    docker-compose down
fi

# 2. Create emergency backup tag
EMERGENCY_TAG="emergency-backup-$(date +%Y%m%d-%H%M%S)"
git tag $EMERGENCY_TAG
log_action "Created emergency backup tag: $EMERGENCY_TAG"

# 3. Rollback database if needed
if [ "$2" == "--restore-db" ]; then
    log_action "Database rollback requested..."
    cd backend
    if [ -f "alembic.ini" ]; then
        log_action "Rolling back database migrations..."
        alembic downgrade -1
    fi
    cd ..
fi

# 4. Revert code to rollback point
log_action "Reverting code to: $ROLLBACK_POINT"
git checkout $ROLLBACK_POINT

# 5. Restore previous configuration if exists
if [ -f ".env.backup" ]; then
    log_action "Restoring previous configuration..."
    cp .env.backup .env
fi

# 6. Start services with previous version
log_action "Starting services with previous version..."
if [ -f "docker-compose.yml" ]; then
    docker-compose up -d
else
    log_action "No docker-compose found, starting manually..."
    cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
fi

# 7. Wait and verify services
sleep 10
log_action "Verifying service health..."

# Check if API is responding
if curl -s http://localhost:8000/health > /dev/null; then
    log_action "✅ API health check passed"
else
    log_action "❌ API health check failed"
fi

# 8. Generate rollback report
cat << EOF > rollback-report.txt
=== MEDAI EMERGENCY ROLLBACK REPORT ===
Timestamp: $(date)
Rollback Point: $ROLLBACK_POINT
Emergency Backup Tag: $EMERGENCY_TAG
Database Restored: ${2:-"No"}
Status: $(curl -s http://localhost:8000/health || echo "Service not responding")

Next Steps:
1. Verify all critical functions are working
2. Check logs for any issues: tail -f rollback.log
3. Monitor system for 30 minutes
4. Investigate root cause of original issue
5. Plan fix and re-deployment

Contact: security@medai.com
EOF

log_action "Rollback completed. Report generated: rollback-report.txt"
log_action "🔍 Please verify system functionality and monitor for issues"

echo "=== ROLLBACK COMPLETED ==="
echo "Check rollback-report.txt for details"