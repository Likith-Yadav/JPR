#!/usr/bin/env python
"""
Script to set up the database and migrate data on Railway.
This script will be run during the deployment process.
"""

import os
import subprocess
import sys
import time
import json
from pathlib import Path
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
import dj_database_url

def setup_database():
    """Set up the database and migrate data."""
    print("Setting up database...")
    
    # Get the base directory
    BASE_DIR = Path(__file__).resolve().parent
    
    # Print database configuration (without sensitive info)
    db_url = os.getenv('DATABASE_URL', '')
    if db_url:
        print("Database URL found")
        db_config = dj_database_url.parse(db_url)
        print(f"Database type: {db_config.get('ENGINE', 'unknown')}")
        print(f"Database name: {db_config.get('NAME', 'unknown')}")
        print(f"Database host: {db_config.get('HOST', 'unknown')}")
        print(f"Database port: {db_config.get('PORT', 'unknown')}")
    else:
        print("WARNING: DATABASE_URL not found in environment!")
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_website.settings')
    
    try:
        print("Initializing Django...")
        application = get_wsgi_application()
        print("Django initialized successfully")
    except Exception as e:
        print(f"Error initializing Django: {str(e)}")
        sys.exit(1)
    
    # Try to run migrations with retries
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting to run migrations (attempt {attempt + 1}/{max_retries})...")
            call_command('migrate')
            print("Migrations completed successfully!")
            break
        except Exception as e:
            print(f"Migration attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Exiting...")
                sys.exit(1)
    
    # Check if we have data to load
    data_file = BASE_DIR / "data.json"
    if data_file.exists():
        print("Loading data from data.json...")
        try:
            # Try different encodings to read the file
            encodings = ['utf-8', 'latin-1', 'cp1252']
            data = None
            
            for encoding in encodings:
                try:
                    with open(data_file, 'r', encoding=encoding) as f:
                        data = json.load(f)
                    print(f"Successfully read data.json with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    print(f"Failed to read with {encoding} encoding, trying next...")
                    continue
                except json.JSONDecodeError as e:
                    print(f"JSON decode error with {encoding} encoding: {str(e)}")
                    continue
            
            if data is None:
                print("Failed to read data.json with any encoding")
                return
            
            # Create a temporary file with the correct encoding
            temp_file = BASE_DIR / "temp_data.json"
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False)
                
                # Try to load the data with natural keys to preserve relationships
                call_command('loaddata', str(temp_file), natural_foreign=True, natural_primary=True)
                print("Data loaded successfully!")
            finally:
                # Clean up temporary file
                if temp_file.exists():
                    temp_file.unlink()
                    
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            # Don't exit on data load failure, as the app can still run
    else:
        print("No data.json file found. Skipping data load.")
    
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database() 