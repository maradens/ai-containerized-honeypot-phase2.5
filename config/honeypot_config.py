#!/usr/bin/env python3
"""
Configuration loader for honeypot scripts
Loads settings from .env file or uses defaults
"""

import os
from dotenv import load_dotenv

def get_config():
    """Load configuration from .env or use defaults"""
    # Try to load .env file
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    
    config = {
        'container_name': os.getenv('CONTAINER_NAME', 'honeypot-manual-test'),
        'image_name': os.getenv('IMAGE_NAME', 'honeypot-ubuntu'),
        'ssh_host': os.getenv('SSH_HOST', 'localhost'),
        'ssh_port': int(os.getenv('SSH_PORT', '2225')),
        'ssh_user': os.getenv('SSH_USER', 'root'),
        'ssh_password': os.getenv('SSH_PASSWORD', 'password123'),
        'backup_dir': os.getenv('BACKUP_DIR', '/home/maradens/github-repos/ai-containerized-honeypot-phase2.5/backups'),
        'vm_ssh_host': os.getenv('VM_SSH_HOST', '192.168.101.192'),
        'vm_ssh_user': os.getenv('VM_SSH_USER', 'hermes'),
        'vm_ssh_port': int(os.getenv('VM_SSH_PORT', '22')),
    }
    
    return config
