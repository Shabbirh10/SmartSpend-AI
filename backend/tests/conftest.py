import pytest
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db

TEST_DB_PATH = "test_smartspend.db"

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY = {
        'broker_url': 'redis://localhost:6379/9',
        'result_backend': 'redis://localhost:6379/9',
    }
    CACHE_TYPE = 'NullCache'
    RATELIMIT_ENABLED = False
    SECRET_KEY = 'test-key'

@pytest.fixture(scope="session")
def event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

@pytest.fixture(scope="session")
def app():
    # Cleanup test db from previous run if any
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except:
            pass
            
    app = create_app(TestConfig)
    
    # Initialize DB Schema once for the entire session
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_async_engine(db_uri)
    
    async def _init_db():
        async with engine.begin() as conn:
            await conn.run_sync(db.metadata.create_all)
    
    asyncio.run(_init_db())
    
    yield app
    
    # Cleanup DB Schema at the end of the session
    async def _drop_db():
        async with engine.begin() as conn:
            await conn.run_sync(db.metadata.drop_all)
        await engine.dispose()
        
    asyncio.run(_drop_db())
    
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except:
            pass

@pytest.fixture(scope="function")
def client(app):
    with app.test_client() as client:
        yield client
        
    # Clean database tables (truncate) after each test function runs
    from app.models import async_session
    async def _cleanup_tables():
        async with async_session() as session:
            # transaction and statement are SQL keywords, so we quote them
            await session.execute(text('DELETE FROM "transaction";'))
            await session.execute(text('DELETE FROM "statement";'))
            await session.commit()
            
    asyncio.run(_cleanup_tables())
