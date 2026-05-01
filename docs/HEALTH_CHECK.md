# 🔧 Health Check & Restore Script

## Overview

`health_check.sh` provides automated health monitoring and one-command restoration for the honeypot system.

## Usage

```bash
# Check overall status
./health_check.sh status

# Run full health check
./health_check.sh check

# Restore to clean state
./health_check.sh restore
```

## Health Check Components

### 1. Container Status
- Verifies container is running
- Checks container name: `honeypot-manual-test`

### 2. SSH Service
- Confirms SSH is listening on port 22
- Critical for honeypot functionality

### 3. Fake Services
- Checks `mysql` fake service exists
- Checks `netstat` fake service exists
- Checks `ps` fake service exists

### 4. Fake Data
- Verifies AWS credentials present
- Verifies SSH keys present
- Verifies fake users created (developer, admin, etc.)

### 5. Database
- Checks if `data/attacks.db` exists
- Verifies database integrity
- ⚠️ Warning is normal if database doesn't exist yet

### 6. Realism Check (CRITICAL!)
- Scans MySQL output for "Fake" text
- Scans netstat output for "Fake" text
- ✗ FAIL means honeypot will be detected by attackers

## Restore Process

When the honeypot is compromised or broken, restore it:

```bash
./health_check.sh restore
```

**What it does:**
1. Backs up current database (preserves attack data)
2. Stops and removes corrupted container
3. Deploys fresh container
4. Re-injects all fake data
5. Re-injects all fake services
6. Verifies restoration with health check

**Result:** Clean honeypot in 2-3 minutes

## Backup Location

```
~/ai-containerized-honeypot-phase2.5/backups/
├── attacks_20260417_103045.db
├── attacks_20260417_145622.db
└── ...
```

Database backups are automatically created before each restore.

## Common Issues

### "Container NOT RUNNING"
```bash
./health_check.sh restore
```

### "SSH NOT listening"
```bash
# Check container is running
docker ps

# If running, SSH might be crashed
docker exec honeypot-manual-test /sbin/init

# If still broken, restore
./health_check.sh restore
```

### "Fake text found in output"
```bash
# See DEPLOYMENT_ISSUES.md Issue #16
# Fix manually or restore:
./health_check.sh restore
```

### "Fake services MISSING"
```bash
# Re-inject only:
cd ~/ai-containerized-honeypot-phase2.5
source venv/bin/activate
python inject_fake_services.py
```

### "Fake data MISSING"
```bash
# Re-inject only:
cd ~/ai-containerized-honeypot-phase2.5
source venv/bin/activate
python fake_data_injector.py
python continue_fake_files.py
```

## Maintenance Schedule

| Frequency | Action | Command |
|-----------|--------|---------|
| Daily | Quick status | `./health_check.sh status` |
| Weekly | Full check | `./health_check.sh check` |
| As needed | Restore | `./health_check.sh restore` |

## Exit Codes

- `0` - All checks passed
- `1` - One or more checks failed

## Notes

- Database not existing is OK (will be created on first `attack_logger.py scan`)
- All restore operations backup the database first
- Fake data and services are re-injected automatically
- Backup directory is created if it doesn't exist
- Script is idempotent (safe to run multiple times)
