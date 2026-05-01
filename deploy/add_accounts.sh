#!/bin/bash
#
# Add Additional User Accounts to Honeypot
# Usage: ./add_accounts.sh
#
# Adds common default credentials that attackers frequently try:
# - ubuntu/ubuntu
# - admin/password
#

CONTAINER="honeypot-manual-test"

echo "🔐 Adding Additional User Accounts"
echo "=================================="
echo ""

# Add ubuntu user with password ubuntu
echo "1. Adding ubuntu/ubuntu..."
docker exec $CONTAINER bash -c "useradd -m -s /bin/bash ubuntu 2>/dev/null || true"
docker exec $CONTAINER bash -c "echo 'ubuntu:ubuntu' | chpasswd"
echo "   ✓ ubuntu/ubuntu created"

# Add/update admin user with password password
echo "2. Adding admin/password..."
docker exec $CONTAINER bash -c "useradd -m -s /bin/bash admin 2>/dev/null || true"
docker exec $CONTAINER bash -c "echo 'admin:password' | chpasswd"
echo "   ✓ admin/password created"

# Verify users exist
echo ""
echo "3. Verifying new users..."
docker exec $CONTAINER bash -c "grep -E '^(ubuntu|admin):' /etc/passwd"

echo ""
echo "=================================="
echo "✅ Complete User Account List:"
echo "=================================="
echo "  root      / password123     (Superuser)"
echo "  ubuntu    / ubuntu          (Common default)"
echo "  admin     / password        (Generic admin)"
echo "  developer / Dev@123456      (Developer)"
echo "  webmaster / (locked)        (Recon only)"
echo "  backup    / (locked)        (Recon only)"
echo "  deploy    / (locked)        (Recon only)"
echo ""
echo "Total: 8 accounts (6 with passwords, 2 locked)"
echo ""
echo "All accounts have access to the same fake data!"
echo "=================================="
