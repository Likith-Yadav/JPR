#!/usr/bin/env python
"""
Script to set up the database and migrate data on Railway.
This script will be run during the deployment process.
"""

import os
import subprocess
import sys
from pathlib import Path

def setup_database():
    """Set up the database and migrate data."""
    print("Setting up database...")
    
    # Get the base directory
    BASE_DIR = Path(__file__).resolve().parent
    
    # Run migrations
    print("Running migrations...")
    subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
    
    # Check if we have data to load
    data_file = BASE_DIR / "data.json"
    if data_file.exists():
        print("Loading data from data.json...")
        subprocess.run([sys.executable, "manage.py", "loaddata", str(data_file)], check=True)
        print("Data loaded successfully!")
    else:
        print("No data.json file found. Skipping data load.")
    
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database() 