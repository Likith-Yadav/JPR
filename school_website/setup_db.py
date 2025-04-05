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
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting to run migrations (attempt {attempt + 1}/{max_retries})...")
            subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
            print("Migrations completed successfully!")
            break
        except subprocess.CalledProcessError as e:
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
            # First, validate the JSON file
            try:
                with open(data_file, 'r') as f:
                    json.load(f)
                print("Data file is valid JSON")
            except json.JSONDecodeError as e:
                print(f"Error: data.json is not valid JSON: {str(e)}")
                return
            
            # Try to load the data
            result = subprocess.run(
                [sys.executable, "manage.py", "loaddata", str(data_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("Error loading data:")
                print("stdout:", result.stdout)
                print("stderr:", result.stderr)
            else:
                print("Data loaded successfully!")
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            # Don't exit on data load failure, as the app can still run
    else:
        print("No data.json file found. Skipping data load.")
    
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database() 