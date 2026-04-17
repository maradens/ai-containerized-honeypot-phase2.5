#!/bin/bash
#
# Honeypot Health Check & Restore Script
# Usage: ./health_check.sh [check|restore|status]
#
# Operations:
#   check   - Run full health check (default)
#   restore - Restore honeypot to clean state
#   status  - Show quick status only
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="honeypot-manual-test"
CONTAINER_IMAGE="honeypot-ubuntu:latest"
DB_PATH="./data/attacks.db"
PROJECT_DIR="$(dirname "$0")"
BACKUP_DIR="$(dirname "$0")/backups"

# Functions
log() { echo -e "$1"; }
log_success() { log "${GREEN}✓${NC} $1"; }
log_error() { log "${RED}✗${NC} $1"; }
log_warning() { log "${YELLOW}⚠${NC} $1"; }

# Check if container is running
check_container_running() {
    docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
}

# Check if SSH is responding inside container
check_ssh_service() {
    docker exec $CONTAINER_NAME netstat -tulpn 2>/dev/null | grep -q ':22 '
}

# Check fake services exist
check_fake_services() {
    local ok=true
    docker exec $CONTAINER_NAME which mysql > /dev/null 2>&1 || { log_error "MySQL MISSING"; ok=false; }
    docker exec $CONTAINER_NAME which netstat > /dev/null 2>&1 || { log_error "netstat MISSING"; ok=false; }
    docker exec $CONTAINER_NAME which ps > /dev/null 2>&1 || { log_error "ps MISSING"; ok=false; }
    [ "$ok" = true ]
}

# Check fake data exists
check_fake_data() {
    local ok=true
    docker exec $CONTAINER_NAME test -f /root/.aws/credentials || { log_error "AWS credentials MISSING"; ok=false; }
    docker exec $CONTAINER_NAME test -f /root/.ssh/id_rsa || { log_error "SSH keys MISSING"; ok=false; }
    docker exec $CONTAINER_NAME grep -q "^developer:" /etc/passwd || { log_error "Fake users MISSING"; ok=false; }
    [ "$ok" = true ]
}

# Check database exists and is valid
check_database() {
    if [ -f "$DB_PATH" ]; then
        if sqlite3 $DB_PATH "SELECT 1;" > /dev/null 2>&1; then
            local count=$(sqlite3 $DB_PATH "SELECT COUNT(*) FROM auth_attempts;" 2>/dev/null || echo "0")
            log_success "Database OK ($count attacks logged)"
            return 0
        else
            log_error "Database CORRUPTED"
            return 1
        fi
    else
        log_warning "Database not found (will be created on first scan)"
        return 0
    fi
}

# Check for "Fake" text in service outputs
check_realistic_output() {
    local fake=false
    if docker exec $CONTAINER_NAME mysql --version 2>/dev/null | grep -qi "fake"; then
        log_error "MySQL output contains 'Fake' text!"
        fake=true
    fi
    if docker exec $CONTAINER_NAME netstat -tulpn 2>/dev/null | grep -qi "fake"; then
        log_error "netstat output contains 'Fake' text!"
        fake=true
    fi
    if [ "$fake" = true ]; then
        log_error "CRITICAL: Services showing 'Fake' text - see DEPLOYMENT_ISSUES.md Issue #16"
        return 1
    fi
    log_success "Service outputs are realistic"
    return 0
}

# Full health check
run_health_check() {
    echo "============================"
    echo "🐝 Honeypot Health Check"
    echo "============================"
    local issues=0
    
    echo ""
    echo "1. Container Status"
    echo "-------------------"
    if check_container_running; then
        log_success "Container running"
    else
        log_error "Container NOT running"
        ((issues++))
    fi
    
    echo ""
    echo "2. SSH Service"
    echo "--------------"
    if check_ssh_service; then
        log_success "SSH listening on port 22"
    else
        log_error "SSH NOT listening"
        ((issues++))
    fi
    
    echo ""
    echo "3. Fake Services"
    echo "----------------"
    if check_fake_services; then
        log_success "All services present"
    else
        ((issues++))
    fi
    
    echo ""
    echo "4. Fake Data"
    echo "------------"
    if check_fake_data; then
        log_success "All data present"
    else
        ((issues++))
    fi
    
    echo ""
    echo "5. Database"
    echo "-----------"
    check_database || ((issues++))
    
    echo ""
    echo "6. Realism Check"
    echo "----------------"
    check_realistic_output || ((issues++))
    
    echo ""
    echo "============================"
    if [ $issues -eq 0 ]; then
        log_success "ALL CHECKS PASSED ✓"
    else
        log_error "$issues ISSUE(S) FOUND ✗"
    fi
    echo "============================"
    
    return $issues
}

# Quick status
show_status() {
    echo "🐝 Honeypot Status"
    echo "=================="
    
    if check_container_running 2>/dev/null; then
        echo "✓ Container: RUNNING"
    else
        echo "✗ Container: STOPPED"
    fi
    
    if [ -f "$DB_PATH" ]; then
        local count=$(sqlite3 $DB_PATH "SELECT COUNT(*) FROM auth_attempts;" 2>/dev/null || echo "0")
        echo "✓ Database: $count attacks logged"
    else
        echo "✗ Database: Not created yet"
    fi
    
    echo ""
}

# Restore honeypot to clean state
restore_honeypot() {
    echo "============================"
    echo "🔄 Honeypot Restore"
    echo "============================"
    
    echo ""
    echo "Step 1: Backup current database..."
    echo "-----------------------------------"
    mkdir -p "$BACKUP_DIR"
    if [ -f "$DB_PATH" ]; then
        local timestamp=$(date +%Y%m%d_%H%M%S)
        cp "$DB_PATH" "$BACKUP_DIR/attacks_${timestamp}.db"
        log_success "Database backed up to backups/attacks_${timestamp}.db"
    else
        log_warning "No database to backup"
    fi
    
    echo ""
    echo "Step 2: Remove old container..."
    echo "--------------------------------"
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    log_success "Old container removed"
    
    echo ""
    echo "Step 3: Deploy new container..."
    echo "--------------------------------"
    cd "$PROJECT_DIR"
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    python honeypot_manager.py deploy 22
    log_success "Container deployed on port 22"
    
    echo ""
    echo "Step 4: Inject fake data..."
    echo "----------------------------"
    python fake_data_injector.py && log_success "Users/AWS/SSH keys injected"
    python inject_fake_services.py && log_success "Fake services injected"
    python continue_fake_files.py 2>/dev/null && log_success "Enhanced files injected" || true
    
    echo ""
    echo "Step 5: Verify restoration..."
    echo "------------------------------"
    sleep 3
    run_health_check
    local result=$?
    
    echo ""
    if [ $result -eq 0 ]; then
        log_success "RESTORE COMPLETE ✓"
    else
        log_error "RESTORE INCOMPLETE - $result issues remain ✗"
    fi
    
    return $result
}

# Main entry point
main() {
    local operation="${1:-check}"
    
    case $operation in
        check)
            run_health_check
            exit $?
            ;;
        restore)
            restore_honeypot
            exit $?
            ;;
        status)
            show_status
            exit 0
            ;;
        *)
            echo "Usage: $0 [check|restore|status]"
            echo ""
            echo "Operations:"
            echo "  check   - Run full health check (default)"
            echo "  restore - Restore honeypot to clean state"
            echo "  status  - Show quick status only"
            exit 1
            ;;
    esac
}

# Run
main "$@"
