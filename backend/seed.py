import asyncio
from app import create_app
from datetime import datetime, timedelta
import random

app = create_app()

async def seed_db():
    with app.app_context():
        # Import dynamically to ensure init_async_db has set global async_session
        from app.models import async_session, Statement, Transaction
        
        print("Seeding database...")
        async with async_session() as session:
            stmt = Statement(filename="demo_seed_data", bank_name="Demo Bank")
            session.add(stmt)
            await session.flush() # Flush to get statement ID
            
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
                t_date = (datetime.now() - timedelta(days=random.randint(1, 30))).date()
                t = Transaction(
                    statement_id=stmt.id,
                    date=t_date,
                    description=desc,
                    amount=output_amt,
                    category=cat,
                    is_anomaly=(output_amt > 1000)
                )
                session.add(t)
            
            await session.commit()
            print("Database seeded asynchronously and committed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_db())
