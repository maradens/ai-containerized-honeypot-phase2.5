#!/usr/bin/env python3
"""
Fixed Fake Data Injection - Uses docker cp for reliable file transfer
"""

import docker
import os
import shutil

def inject_files():
    client = docker.from_env()
    container = client.containers.get("honeypot-manual-test")
    
    print("🔧 Fixing fake data injection using docker cp...")
    
    # Source directory
    src_dir = "/home/maradens/.openclaw/workspace/ai-honeypot-phase1/fake_files"
    
    # Files to copy
    files = {
        "aws_credentials": [
            ("/root/.aws/credentials", "root:root"),
            ("/home/admin/.aws/credentials", "admin:admin"),
            ("/home/developer/.aws/credentials", "developer:developer"),
            ("/home/deploy/.aws/credentials", "deploy:deploy"),
        ],
        "env_file": [
            ("/var/www/html/.env", "root:root"),
            ("/home/admin/.env", "admin:admin"),
            ("/home/developer/.env", "developer:developer"),
        ],
        "git_credentials": [
            ("/root/.git-credentials", "root:root"),
            ("/home/admin/.git-credentials", "admin:admin"),
            ("/home/developer/.git-credentials", "developer:developer"),
        ],
        "kube_config": [
            ("/root/.kube/config", "root:root"),
            ("/home/admin/.kube/config", "admin:admin"),
            ("/home/deploy/.kube/config", "deploy:deploy"),
        ],
        "id_rsa": [
            ("/root/.ssh/id_rsa", "root:root"),
            ("/home/admin/.ssh/id_rsa", "admin:admin"),
            ("/home/developer/.ssh/id_rsa", "developer:developer"),
        ],
    }
    
    for filename, destinations in files.items():
        src_file = os.path.join(src_dir, filename)
        if os.path.exists(src_file):
            for dest_path, ownership in destinations:
                # Create directory
                container.exec_run(f"mkdir -p {os.path.dirname(dest_path)}")
                
                # Copy file
                container.put_archive(os.path.dirname(dest_path), 
                                   create_tar_archive(src_file, os.path.basename(dest_path)))
                
                # Set permissions
                container.exec_run(f"chown {ownership} {dest_path}")
                container.exec_run(f"chmod 600 {dest_path}")
                
                print(f"  ✓ {dest_path}")
        else:
            print(f"  ✗ {filename} not found")
    
    print("\n✅ Injection complete!")
    
def create_tar_archive(file_path, arcname=None):
    """Create a tar archive from a file"""
    import tarfile
    import io
    
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
        tar.add(file_path, arcname=arcname or os.path.basename(file_path))
    tar_buffer.seek(0)
    return tar_buffer.read()

if __name__ == "__main__":
    inject_files()
