import os
import subprocess
import sys
from backup_db import backup_database
from restore_db import restore_database

def deploy():
    # Step 1: Backup the database
    print("Backing up database...")
    backup_database()
    
    # Step 2: Run git commands
    print("Running git commands...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Update website"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Git commands completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error during git commands: {e}")
        return
    
    # Step 3: Restore the database
    print("Restoring database...")
    restore_database()
    
    print("Deployment completed successfully")

if __name__ == "__main__":
    deploy() 