import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite+aiosqlite:///smartspend.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Celery configuration
    CELERY = {
        'broker_url': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        'result_backend': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        'task_ignore_result': False,
    }
    
    # Caching configuration
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    CACHE_REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    CACHE_REDIS_DB = 1
    CACHE_DEFAULT_TIMEOUT = 300
