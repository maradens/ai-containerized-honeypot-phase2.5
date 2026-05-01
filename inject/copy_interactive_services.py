#!/usr/bin/env python3
"""
Copy interactive services to container
"""

from honeypot_config import get_config
import docker
import tarfile
import io
import os

def create_tar_archive(file_path, arcname=None):
    """Create a tar archive from a file"""
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
        tar.add(file_path, arcname=arcname or os.path.basename(file_path))
    tar_buffer.seek(0)
    return tar_buffer.read()

def copy_services():
    client = docker.from_env()
    container = client.containers.get(get_config()["container_name"])
    
    print("🎭 Copying interactive services...")
    
    services_dir = "/home/maradens/.openclaw/workspace/ai-honeypot-phase1/interactive_services"
    
    services = [
        ("mysql", "/usr/local/bin/mysql"),
        ("redis-cli", "/usr/local/bin/redis-cli"),
        ("psql", "/usr/local/bin/psql"),
    ]
    
    for service_name, dest_path in services:
        src_path = os.path.join(services_dir, service_name)
        
        if os.path.exists(src_path):
            # Create tar archive
            tar_data = create_tar_archive(src_path, os.path.basename(dest_path))
            
            # Copy to container
            container.put_archive(os.path.dirname(dest_path), tar_data)
            container.exec_run(f"chmod +x {dest_path}")
            print(f"  ✓ {service_name} installed at {dest_path}")
        else:
            print(f"  ✗ {service_name} not found")
    
    print("\n✅ Interactive services installed!")
    print("\n📝 Test these commands:")
    print("   mysql          → Interactive MySQL")
    print("   redis-cli      → Interactive Redis")
    print("   psql           → Interactive PostgreSQL")
    print("\nTry these queries:")
    print("   In MySQL: SELECT * FROM users")
    print("   In Redis: GET password")
    print("   In PostgreSQL: SELECT * FROM credentials")

if __name__ == "__main__":
    copy_services()
