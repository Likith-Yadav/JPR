#!/usr/bin/env python
"""
Script to dump data from SQLite database to JSON file.
"""

import os
import subprocess
import sys
from pathlib import Path
import json
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

def dump_data():
    """Dump data from SQLite database to JSON file."""
    print("Dumping data from SQLite database...")
    
    # Get the base directory
    BASE_DIR = Path(__file__).resolve().parent
    
    # Force SQLite database for dumping
    os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_website.settings')
    application = get_wsgi_application()
    
    # Create fixtures directory if it doesn't exist
    fixtures_dir = BASE_DIR / 'fixtures'
    fixtures_dir.mkdir(exist_ok=True)
    
    # Dump all data to JSON
    try:
        with open(BASE_DIR / 'data.json', 'w', encoding='utf-8') as f:
            call_command('dumpdata', format='json', indent=2, stdout=f)
        print("Data successfully dumped to data.json")
    except Exception as e:
        print(f"Error dumping data: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    dump_data() 