from app import create_app

app = create_app()
celery = app.extensions["celery"]

# Import tasks module to register Celery tasks on worker startup
import app.tasks
