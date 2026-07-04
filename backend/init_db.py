import os
import sys
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

# Add parent directory to path to enable app imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db

async def async_init():
    app = create_app()
    with app.app_context():
        # Get the database engine configuration
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        
        # Ensure instance directory exists if using SQLite
        if "sqlite" in db_uri:
            os.makedirs(os.path.join(app.root_path, '../instance'), exist_ok=True)
            
        print(f"Initializing database at: {db_uri}")
        engine = create_async_engine(db_uri)
        
        # Create all tables asynchronously
        async with engine.begin() as conn:
            await conn.run_sync(db.metadata.create_all)
            
        print("Database schema initialized successfully!")
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(async_init())
