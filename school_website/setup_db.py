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

def setup_database():
    """Set up the database and migrate data."""
    print("Setting up database...")
    
    # Get the base directory
    BASE_DIR = Path(__file__).resolve().parent
    
    # Try to run migrations with retries
    max_retries = 5
    retry_delay = 10  # Increased delay to allow for connection establishment
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting to run migrations (attempt {attempt + 1}/{max_retries})...")
            # Print current DATABASE_URL (with password masked)
            db_url = os.getenv('DATABASE_URL', '')
            if db_url:
                masked_url = db_url.replace(db_url.split('@')[0].split(':')[-1], '****')
                print(f"Using database URL: {masked_url}")
            
            result = subprocess.run(
                [sys.executable, "manage.py", "migrate"],
                capture_output=True,
                text=True,
                check=False  # Don't raise exception, we'll handle it
            )
            
            if result.returncode == 0:
                print("Migrations completed successfully!")
                break
            else:
                print(f"Migration failed with error:")
                print(result.stderr)
                if "OperationalError" in result.stderr and attempt < max_retries - 1:
                    print(f"Database connection failed. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print("Migration failed with non-connection error:")
                    print(result.stderr)
                    sys.exit(1)
                    
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
                
                # Try to load the data with retries
                for attempt in range(max_retries):
                    result = subprocess.run(
                        [sys.executable, "manage.py", "loaddata", str(temp_file)],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        print("Data loaded successfully!")
                        break
                    else:
                        print(f"Error loading data (attempt {attempt + 1}/{max_retries}):")
                        print("stdout:", result.stdout)
                        print("stderr:", result.stderr)
                        if attempt < max_retries - 1:
                            print(f"Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                        else:
                            print("Failed to load data after all retries")
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