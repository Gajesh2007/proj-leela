#!/usr/bin/env python
"""
Initialize databases and storage for Project Leela.
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
from leela.knowledge_representation.neo4j_connector import Neo4jConnector
from leela.config import get_config


async def initialize_database():
    """Initialize the database schema."""
    try:
        print("Initializing databases...")
        
        # Get config and create data dir if necessary
        config = get_config()
        data_dir = Path(config["paths"]["data_dir"])
        os.makedirs(data_dir, exist_ok=True)
        
        # Step 1: Create SQLite database
        print("\n=== Setting up SQLite database ===")
        db_manager = DatabaseManager()
        await db_manager.initialize_db()
        print(f"SQLite database created successfully at {data_dir / 'leela.db'}!")
        
        # Step 2: Initialize Neo4j connector (or in-memory implementation)
        print("\n=== Setting up Neo4j connector ===")
        neo4j_connector = Neo4jConnector()
        connected = await neo4j_connector.connect()
        
        if connected:
            print("Successfully connected to Neo4j")
            await neo4j_connector.initialize_schema()
            await neo4j_connector.close()
        else:
            print("Failed to connect to Neo4j, but in-memory implementation is available")

        print("\nDatabase initialization complete!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(initialize_database())