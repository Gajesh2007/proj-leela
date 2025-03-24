#!/usr/bin/env python
"""
Simple script to create the database schema for Project Leela.
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the parent directory to sys.path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from leela.data_persistence.db_interface import Base, DatabaseManager


async def initialize_database():
    """Initialize the database schema."""
    try:
        print("Initializing database...")
        
        # Create database manager
        db_manager = DatabaseManager()
        
        # Create all tables
        await db_manager.initialize_db()
        
        print("Database schema created successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(initialize_database())