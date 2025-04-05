import os
import shutil
from datetime import datetime

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
    
    # Copy the database file
    if os.path.exists(db_file):
        shutil.copy2(db_file, backup_file)
        print(f"Database backed up to {backup_file}")
    else:
        print("Database file not found")

if __name__ == "__main__":
    backup_database() 