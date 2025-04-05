#!/usr/bin/env python
"""
Database migration helper script.
This script helps with migrating data from SQLite to PostgreSQL.
"""

import os
import sys
import json
import subprocess
from datetime import datetime

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import django
        import dj_database_url
        import psycopg2
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install django dj-database-url psycopg2-binary")
        return False

def dump_sqlite_data():
    """Dump data from SQLite database to JSON files."""
    print("Dumping data from SQLite database...")
    
    # Create fixtures directory if it doesn't exist
    if not os.path.exists('fixtures'):
        os.makedirs('fixtures')
    
    # Get list of apps with models
    result = subprocess.run(
        ['python', 'manage.py', 'dumpdata', '--exclude', 'auth.permission', '--exclude', 'contenttypes', '--indent', '2'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Save the output to a file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'fixtures/data_dump_{timestamp}.json'
        with open(filename, 'w') as f:
            f.write(result.stdout)
        print(f"Data dumped to {filename}")
        return filename
    else:
        print(f"Error dumping data: {result.stderr}")
        return None

def load_data_to_postgres(json_file):
    """Load data from JSON file to PostgreSQL database."""
    if not json_file or not os.path.exists(json_file):
        print("No data file found to load.")
        return False
    
    print(f"Loading data from {json_file} to PostgreSQL...")
    
    result = subprocess.run(
        ['python', 'manage.py', 'loaddata', json_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("Data loaded successfully!")
        return True
    else:
        print(f"Error loading data: {result.stderr}")
        return False

def main():
    """Main function to handle the migration process."""
    if not check_dependencies():
        return
    
    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        print("DATABASE_URL environment variable is not set.")
        print("Please set it to your PostgreSQL connection string.")
        print("Example: export DATABASE_URL=postgres://username:password@host:port/database")
        return
    
    # Dump data from SQLite
    json_file = dump_sqlite_data()
    
    if json_file:
        # Load data to PostgreSQL
        load_data_to_postgres(json_file)
    
    print("\nMigration process completed!")

if __name__ == "__main__":
    main() 