from app import create_app, db
from app.models import Statement, Transaction

app = create_app()

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
