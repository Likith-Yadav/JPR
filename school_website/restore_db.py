import os
import shutil
import glob

def restore_database():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Target database file
    db_file = os.path.join(current_dir, 'db.sqlite3')
    
    # Backups directory
    backups_dir = os.path.join(current_dir, 'backups')
    
    # Find the most recent backup
    backup_files = glob.glob(os.path.join(backups_dir, 'db_backup_*.sqlite3'))
    
    if not backup_files:
        print("No backup files found")
        return
    
    # Sort by modification time (most recent first)
    latest_backup = max(backup_files, key=os.path.getmtime)
    
    # Restore the database
    shutil.copy2(latest_backup, db_file)
    print(f"Database restored from {latest_backup}")

if __name__ == "__main__":
    restore_database() 