#!/usr/bin/env python
"""
Script to initialize the database for Project Leela.
"""
import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from leela.data_persistence.repository import Repository
from leela.utils.logging import LeelaLogger

logger = LeelaLogger.get_logger("scripts.create_db")


async def initialize_database():
    """Initialize the database."""
    try:
        logger.info("Initializing database...")
        
        # Create repository and initialize schema
        repository = Repository()
        await repository.initialize()
        
        logger.info("Database initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)


def run_alembic_migrations():
    """Run Alembic migrations."""
    try:
        logger.info("Running Alembic migrations...")
        
        # Generate migration
        migration_result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "Initial migration"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Migration created: {migration_result.stdout.strip()}")
        
        # Apply migration
        upgrade_result = subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Migration applied: {upgrade_result.stdout.strip()}")
        
        logger.info("Alembic migrations completed successfully!")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running Alembic command: {e}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        sys.exit(1)


async def main():
    """Main function."""
    logger.info("Beginning database setup...")
    
    # Initialize database
    await initialize_database()
    
    # Run Alembic migrations
    run_alembic_migrations()
    
    logger.info("Database setup complete!")


if __name__ == "__main__":
    asyncio.run(main())