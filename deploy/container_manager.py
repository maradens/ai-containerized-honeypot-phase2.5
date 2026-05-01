#!/usr/bin/env python3
"""
Container Manager - Reset, backup, and deploy honeypot containers
"""

from honeypot_config import get_config
import docker
import json
import os
from datetime import datetime
import subprocess

class ContainerManager:
    def __init__(self, container_name=get_config()["container_name"], image_name="honeypot-ubuntu"):
        self.client = docker.from_env()
        self.container_name = container_name
        self.image_name = image_name
        self.backup_dir = "/home/maradens/.openclaw/workspace/ai-honeypot-phase1/backups"
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def backup_container_state(self):
        """Backup container data before reset"""
        print("💾 Backing up container state...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        
        # Copy important files
        files_to_backup = [
            "/var/log/attacks/command_log",
            "/var/log/attacks/command_log",
            "/root/.bash_history",
            "/home/admin/.bash_history",
            "/home/developer/.bash_history",
        ]
        
        container = self.client.containers.get(self.container_name)
        
        for file_path in files_to_backup:
            try:
                result = container.exec_run(f"cat {file_path} 2>/dev/null")
                if result.output:
                    local_path = os.path.join(backup_path, file_path.lstrip('/'))
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    with open(local_path, 'wb') as f:
                        f.write(result.output)
                    print(f"  ✓ Backed up {file_path}")
            except:
                pass
        
        # Backup auth logs from database
        try:
            from attack_logger import AttackLogger
            logger = AttackLogger()
            export_path = os.path.join(backup_path, "auth_attempts.json")
            logger.export_to_json(export_path)
            print(f"  ✓ Backed up auth attempts to {export_path}")
        except Exception as e:
            print(f"  ⚠ Could not backup auth data: {e}")
        
        print(f"\n✅ Backup saved to: {backup_path}")
        return backup_path
        
    def reset_container(self, keep_logs=False):
        """Reset container to clean state"""
        print("\n🔄 Resetting container...")
        
        # 1. Backup first
        if keep_logs:
            self.backup_container_state()
        
        # 2. Stop container
        try:
            container = self.client.containers.get(self.container_name)
            container.stop(timeout=10)
            print("  ✓ Container stopped")
        except docker.errors.NotFound:
            print("  ⚠ Container not found, will create new one")
        
        # 3. Remove container
        try:
            container.remove(force=True)
            print("  ✓ Container removed")
        except:
            pass
        
        # 4. Create fresh container
        print("  → Creating fresh container...")
        self.deploy_container()
        
        print("\n✅ Container reset complete!")
        
    def deploy_container(self, port=2225):
        """Deploy a fresh honeypot container"""
        print(f"\n🚀 Deploying honeypot container on port {port}...")
        
        # Check if image exists
        try:
            self.client.images.get(self.image_name)
            print(f"  ✓ Image {self.image_name} exists")
        except docker.errors.ImageNotFound:
            print(f"  ✗ Image {self.image_name} not found!")
            print("  → Please build the image first:")
            print("     docker build -t honeypot-ubuntu .")
            return
        
        # Remove existing container if exists
        try:
            old_container = self.client.containers.get(self.container_name)
            old_container.stop(timeout=10)
            old_container.remove(force=True)
            print("  ✓ Removed old container")
        except docker.errors.NotFound:
            pass
        
        # Create new container
        container = self.client.containers.run(
            self.image_name,
            name=self.container_name,
            detach=True,
            ports={
                '22/tcp': port,
            },
            volumes={
                self.backup_dir: {
                    'bind': '/backups',
                    'mode': 'rw'
                }
            },
            environment={
                'CONTAINER_NAME': self.container_name,
                'HONEYPOT_PORT': str(port),
            },
            restart_policy={
                'Condition': 'unless-stopped'
            },
        )
        
        print(f"  ✓ Container created: {self.container_name}")
        print(f"  ✓ Container ID: {container.short_id}")
        print(f"  ✓ Access: ssh root@localhost -p {port}")
        
        # Wait for container to be ready
        container.wait(condition='running')
        print("  ✓ Container is running")
        
        # Re-inject fake data and services
        print("\n  → Re-injecting fake data...")
        self.inject_fake_data()
        
        print(f"\n✅ Deployment complete!")
        print(f"   Container: {self.container_name}")
        print(f"   Port: {port}")
        print(f"   Access: ssh root@localhost -p {port}")
        
    def inject_fake_data(self):
        """Re-inject all fake data and services"""
        import subprocess
        
        scripts = [
            "attack_logger.py",
            "fake_files_enhanced.py",
            "copy_interactive_services.py",
        ]
        
        for script in scripts:
            script_path = f"/home/maradens/.openclaw/workspace/ai-honeypot-phase1/{script}"
            if os.path.exists(script_path):
                print(f"  → Running {script}...")
                subprocess.run(
                    ["python3", script_path],
                    cwd="/home/maradens/.openclaw/workspace/ai-honeypot-phase1",
                    capture_output=True,
                    text=True
                )
                print(f"  ✓ {script} complete")
    
    def check_container_health(self):
        """Check if container needs reset"""
        print("\n🏥 Checking container health...")
        
        try:
            container = self.client.containers.get(self.container_name)
            
            # Check uptime
            start_time = container.attrs['HostConfig']['StartedAt']
            uptime_hours = (datetime.now() - datetime.fromisoformat(start_time.replace('Z', '+00:00'))).total_seconds() / 3600
            
            print(f"  Uptime: {uptime_hours:.1f} hours")
            
            # Check for suspicious activity
            result = container.exec_run("wc -l /var/log/attacks/command_log 2>/dev/null")
            if result.output:
                line_count = int(result.output.decode().split()[0])
                print(f"  Commands logged: {line_count}")
                
                if line_count > 1000:
                    print("  ⚠ HIGH ACTIVITY DETECTED - Consider reset!")
                    return False
            
            # Check for modified files
            result = container.exec_run("find /etc/nginx /home/deploy -mtime -1 2>/dev/null | wc -l")
            if result.output:
                modified_count = int(result.output.decode().split()[0])
                if modified_count > 5:
                    print(f"  ⚠ {modified_count} files modified recently - Consider reset!")
                    return False
            
            print("  ✓ Container looks healthy")
            return True
            
        except Exception as e:
            print(f"  ✗ Error checking health: {e}")
            return False
    
    def schedule_daily_reset(self):
        """Create a cron job for daily reset"""
        cron_job = """# Honeypot container reset - Daily at 3 AM
0 3 * * * cd /home/maradens/.openclaw/workspace/ai-honeypot-phase1 && source venv/bin/activate && python container_manager.py reset --keep-logs >> /var/log/honeypot-reset.log 2>&1
"""
        
        # Write to crontab
        print("\n📅 Setting up daily reset at 3 AM...")
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Append to existing crontab
            current_cron = result.stdout
            if "honeypot-reset" not in current_cron:
                new_cron = current_cron + cron_job
                process = subprocess.Popen(
                    ["crontab", "-"],
                    stdin=subprocess.PIPE,
                    text=True
                )
                process.communicate(input=new_cron)
                print("  ✓ Daily reset scheduled")
            else:
                print("  ✓ Daily reset already scheduled")
        else:
            # Create new crontab
            process = subprocess.Popen(
                ["crontab", "-"],
                stdin=subprocess.PIPE,
                text=True
            )
            process.communicate(input=cron_job)
            print("  ✓ Daily reset scheduled (new crontab)")

def main():
    import sys
    
    manager = ContainerManager()
    
    if len(sys.argv) < 2:
        print("Container Manager for Honeypot")
        print("\nUsage:")
        print("  python container_manager.py status     # Check container health")
        print("  python container_manager.py reset      # Reset container")
        print("  python container_manager.py reset --keep-logs  # Reset with backup")
        print("  python container_manager.py deploy     # Deploy fresh container")
        print("  python container_manager.py schedule   # Schedule daily reset")
        return
    
    command = sys.argv[1]
    
    if command == "status":
        manager.check_container_health()
    elif command == "reset":
        keep_logs = "--keep-logs" in sys.argv
        manager.reset_container(keep_logs=keep_logs)
    elif command == "deploy":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 2225
        manager.deploy_container(port=port)
    elif command == "schedule":
        manager.schedule_daily_reset()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
