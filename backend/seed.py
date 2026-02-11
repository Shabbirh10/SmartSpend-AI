from app import create_app, db
from app.models import Statement, Transaction
from datetime import datetime, timedelta
import random

app = create_app()

def seed_db():
    with app.app_context():
        print("Seeding database...")
        stmt = Statement(filename="demo_seed_data", bank_name="Demo Bank")
        db.session.add(stmt)
        db.session.flush()
        
        txns = [
            ("UBER *RIDE", 25.00, "Transport"),
            ("STARBUCKS", 6.50, "Food"),
            ("AIRBNB", 450.00, "Travel"),
            ("AMAZON PRIME", 139.00, "Shopping"),
            ("KROGER", 120.50, "Groceries"),
            ("CINEMA CITY", 30.00, "Entertainment"),
            ("PAYPAL *EBAY", 45.00, "Shopping"),
            ("LULULEMON", 98.00, "Shopping"),
            ("EXXON MOBIL", 55.00, "Transport"),
            ("HOSPITAL CO-PAY", 50.00, "Health"),
        ]
        
        for desc, output_amt, cat in txns:
            t = Transaction(
                statement_id=stmt.id,
                date=datetime.now() - timedelta(days=random.randint(1, 30)),
                description=desc,
                amount=output_amt,
                category=cat,
                is_anomaly=(output_amt > 1000)
            )
            db.session.add(t)
        
        db.session.commit()
        print("Database seeded with 10 demo transactions!")

if __name__ == "__main__":
    seed_db()
