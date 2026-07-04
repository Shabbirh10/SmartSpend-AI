from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.core.config import Config
from app.models import db, init_async_db
from celery import Celery, Task

# Extensions
migrate = Migrate()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"],
    storage_uri="redis://localhost:6379/2" # Separate Redis DB for rate limiting
)

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config.get("CELERY", {}))
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    CORS(app)
    db.init_app(app)
    init_async_db(app) # Initialize Async SQLAlchemy Engine and Sessionmaker
    migrate.init_app(app, db)
    cache.init_app(app)
    limiter.init_app(app)

    # Initialize Celery
    celery_init_app(app)

    # Security Headers Middleware
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Relaxed Content-Security-Policy to support local development and APIs on localhost and 127.0.0.1
        response.headers['Content-Security-Policy'] = "default-src 'self' http://localhost:3000 http://localhost:8000 http://127.0.0.1:3000 http://127.0.0.1:8000; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self' http://localhost:3000 http://localhost:8000 http://127.0.0.1:3000 http://127.0.0.1:8000;"
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    # Blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'smartspend-ai-backend'}

    return app
