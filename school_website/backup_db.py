import os
import shutil
from datetime import datetime
import sys

def backup_database():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Source database file
    db_file = os.path.join(current_dir, 'db.sqlite3')
    
    # Create backups directory if it doesn't exist
    backups_dir = os.path.join(current_dir, 'backups')
    if not os.path.exists(backups_dir):
        os.makedirs(backups_dir)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backups_dir, f'db_backup_{timestamp}.sqlite3')
    
    try:
        # Copy the database file
        shutil.copy2(db_file, backup_file)
        print(f"Database backed up successfully to: {backup_file}")
        
        # Keep only the last 5 backups
        backup_files = sorted([f for f in os.listdir(backups_dir) if f.startswith('db_backup_')])
        if len(backup_files) > 5:
            for old_backup in backup_files[:-5]:
                os.remove(os.path.join(backups_dir, old_backup))
                print(f"Removed old backup: {old_backup}")
                
    except Exception as e:
        print(f"Error backing up database: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    backup_database() 