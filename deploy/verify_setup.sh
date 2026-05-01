#!/bin/bash
# HONEYPOT PHASE 2.5 - FULL VERIFICATION SCRIPT
# Checks all components after VM migration

echo "=========================================="
echo "HONEYPOT PHASE 2.5 VERIFICATION"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
}

check_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
}

check_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
}

# 1. System Check
echo "1. SYSTEM CHECK"
echo "---------------"
if command -v docker &> /dev/null; then
    check_pass "Docker installed"
    DOCKER_VERSION=$(docker --version)
    echo "   $DOCKER_VERSION"
else
    check_fail "Docker not installed"
fi

# 2. Docker Service
echo ""
echo "2. DOCKER SERVICE"
echo "-----------------"
if systemctl is-active --quiet docker; then
    check_pass "Docker service running"
else
    check_fail "Docker service not running"
fi

# 3. Project Directory
echo ""
echo "3. PROJECT DIRECTORY"
echo "--------------------"
if [ -d "~/ai-honeypot-phase2.5" ]; then
    check_pass "Project directory exists"
    SCRIPT_COUNT=$(ls ~/ai-honeypot-phase2.5/*.py 2>/dev/null | wc -l)
    echo "   Python scripts: $SCRIPT_COUNT"
else
    check_fail "Project directory missing"
fi

# 4. Docker Image
echo ""
echo "4. DOCKER IMAGE"
echo "---------------"
if docker images | grep -q honeypot-ubuntu; then
    check_pass "Honeypot image exists"
    docker images | grep honeypot-ubuntu
else
    check_fail "Honeypot image not found"
fi

# 5. Container Status
echo ""
echo "5. CONTAINER STATUS"
echo "-------------------"
if docker ps -a | grep -q honeypot-prod; then
    CONTAINER_STATUS=$(docker ps -a --filter "name=honeypot-prod" --format "{{.Status}}")
    if docker ps --filter "name=honeypot-prod" --format "{{.Status}}" | grep -q "Up"; then
        check_pass "Container honeypot-prod running"
        docker ps --filter "name=honeypot-prod"
    else
        check_warn "Container honeypot-prod exists but not running"
        docker ps -a --filter "name=honeypot-prod"
    fi
else
    check_fail "Container honeypot-prod not found"
fi

# 6. Port Mapping
echo ""
echo "6. PORT MAPPING"
echo "---------------"
if docker ps -a --filter "name=honeypot-prod" --format "{{.Ports}}" | grep -q "22/tcp"; then
    check_pass "Port 22 mapped (honeypot SSH)"
    docker ps -a --filter "name=honeypot-prod" --format "{{.Ports}}"
else
    check_fail "Port 22 not mapped"
fi

if docker ps -a --filter "name=honeypot-prod" --format "{{.Ports}}" | grep -q "22222/tcp"; then
    check_pass "Port 22222 mapped (admin SSH)"
else
    check_warn "Port 22222 not mapped (admin SSH)"
fi

# 7. Virtual Environment
echo ""
echo "7. VIRTUAL ENVIRONMENT"
echo "----------------------"
if [ -d "~/ai-honeypot-phase2.5/venv" ]; then
    check_pass "Virtual environment exists"
    if [ -f "~/ai-honeypot-phase2.5/venv/bin/python" ]; then
        PYTHON_VERSION=$(~/ai-honeypot-phase2.5/venv/bin/python --version)
        echo "   $PYTHON_VERSION"
    fi
else
    check_fail "Virtual environment missing"
fi

# 8. Dependencies
echo ""
echo "8. DEPENDENCIES"
echo "---------------"
if [ -f "~/ai-honeypot-phase2.5/requirements.txt" ]; then
    check_pass "requirements.txt exists"
    echo "   Required packages:"
    cat ~/ai-honeypot-phase2.5/requirements.txt | sed 's/^/      /'
else
    check_fail "requirements.txt missing"
fi

# 9. Key Scripts
echo ""
echo "9. KEY SCRIPTS"
echo "--------------"
KEY_SCRIPTS=(
    "attack_logger.py"
    "container_manager.py"
    "behavioral_analyzer.py"
    "ttp_analyzer.py"
    "cross_correlation_analyzer.py"
)

for script in "${KEY_SCRIPTS[@]}"; do
    if [ -f "~/ai-honeypot-phase2.5/$script" ]; then
        check_pass "$script exists"
    else
        check_fail "$script missing"
    fi
done

# 10. Cron Jobs
echo ""
echo "10. CRON JOBS"
echo "-------------"
if crontab -l 2>/dev/null | grep -q honeypot; then
    check_pass "Cron jobs installed"
    echo "   Active cron jobs:"
    crontab -l | grep honeypot | sed 's/^/      /'
else
    check_warn "No honeypot cron jobs found"
fi

# 11. Log Directory
echo ""
echo "11. LOG DIRECTORY"
echo "-----------------"
if [ -d "/var/log/honeypot" ]; then
    check_pass "Log directory exists"
    LOG_FILES=$(ls /var/log/honeypot 2>/dev/null | wc -l)
    echo "   Log files: $LOG_FILES"
else
    check_warn "Log directory missing (will be created on first run)"
fi

# 12. Database
echo ""
echo "12. DATABASE"
echo "------------"
if [ -f "~/ai-honeypot-phase2.5/data/attacks.db" ]; then
    check_pass "Database exists"
    DB_SIZE=$(ls -lh ~/ai-honeypot-phase2.5/data/attacks.db | awk '{print $5}')
    echo "   Size: $DB_SIZE"
else
    check_warn "Database not created yet (will create on first scan)"
fi

# 13. Firewall
echo ""
echo "13. FIREWALL"
echo "------------"
if command -v ufw &> /dev/null; then
    UFW_STATUS=$(ufw status | head -1)
    echo "   $UFW_STATUS"
    if ufw status | grep -q "22/tcp"; then
        check_pass "Port 22 allowed"
    fi
    if ufw status | grep -q "22222/tcp"; then
        check_pass "Port 22222 allowed"
    fi
else
    check_warn "ufw not installed"
fi

# 14. Container Health Test
echo ""
echo "14. CONTAINER HEALTH TEST"
echo "-------------------------"
if docker ps --filter "name=honeypot-prod" --format "{{.Status}}" | grep -q "Up"; then
    # Test SSH connectivity
    if timeout 5 bash -c "echo 'test' | ssh -o ConnectTimeout=2 -o BatchMode=yes -p 22 root@localhost" 2>/dev/null; then
        check_pass "SSH on port 22 responsive"
    else
        check_warn "SSH on port 22 not responding (may need password)"
    fi
    
    # Test fake services
    echo "   Testing fake services inside container:"
    if docker exec honeypot-prod ls /usr/local/bin/mysql &>/dev/null; then
        check_pass "MySQL fake service installed"
    fi
    if docker exec honeypot-prod ls /usr/local/bin/redis-cli &>/dev/null; then
        check_pass "Redis fake service installed"
    fi
    if docker exec honeypot-prod ls /usr/local/bin/psql &>/dev/null; then
        check_pass "PostgreSQL fake service installed"
    fi
    if docker exec honeypot-prod ls /usr/local/bin/netstat &>/dev/null; then
        check_pass "Netstat fake service installed"
    fi
    if docker exec honeypot-prod ls /usr/local/bin/ps &>/dev/null; then
        check_pass "PS fake service installed"
    fi
else
    check_fail "Container not running, cannot test"
fi

# 15. Recent Activity
echo ""
echo "15. RECENT ACTIVITY"
echo "-------------------"
if docker ps --filter "name=honeypot-prod" --format "{{.Status}}" | grep -q "Up"; then
    FAILED_COUNT=$(docker exec honeypot-prod lastb 2>/dev/null | grep -c "119.235.251.247" || echo "0")
    echo "   Indonesian attacker (119.235.251.247): $FAILED_COUNT failed attempts"
    
    SUCCESS_COUNT=$(docker exec honeypot-prod last 2>/dev/null | wc -l)
    echo "   Successful logins: $SUCCESS_COUNT"
fi

# Summary
echo ""
echo "=========================================="
echo "VERIFICATION COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. If container not running: python container_manager.py deploy 22"
echo "2. Start monitoring: python attack_logger.py scan"
echo "3. Schedule automation: python container_manager.py schedule"
echo "4. Run analyses:"
echo "   - python behavioral_analyzer.py"
echo "   - python ttp_analyzer.py"
echo "   - python cross_correlation_analyzer.py"
echo ""
echo "🐝 Honeypot Phase 2.5 verification complete!"
