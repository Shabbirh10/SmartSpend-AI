import asyncio
import os
from celery import shared_task
from app.models import async_session, Statement, Transaction
from app.services.parser import parser
from app.services.classifier import classifier

@shared_task(bind=True)
def process_statement_task(self, filepath, filename):
    """
    Celery task to parse and classify transaction statements asynchronously.
    """
    async def _async_process():
        # Open a clean async session
        async with async_session() as session:
            try:
                # 1. Parse PDF (scrubbing is handled inside parser)
                raw_transactions = parser.extract_transactions(filepath)
                
                # 2. Create Statement record
                statement = Statement(filename=filename, bank_name="Unknown")
                session.add(statement)
                await session.flush() # Generate ID
                
                analyzed_data = []
                
                # 3. Categorize and Save Transactions
                for item in raw_transactions:
                    category = classifier.predict(item['description'])
                    is_anomaly = item['amount'] > 1000.0
                    
                    txn = Transaction(
                        statement_id=statement.id,
                        date=item['date'],
                        description=item['description'],
                        amount=item['amount'],
                        category=category,
                        is_anomaly=is_anomaly
                    )
                    session.add(txn)
                    
                    analyzed_data.append({
                        'date': item['date'].isoformat(),
                        'description': item['description'],
                        'amount': item['amount'],
                        'category': category,
                        'is_anomaly': is_anomaly
                    })
                
                await session.commit()
                
                # Remove physical file after successful processing
                if os.path.exists(filepath):
                    os.remove(filepath)
                    
                return {
                    'status': 'SUCCESS',
                    'statement_id': statement.id,
                    'transactions': analyzed_data
                }
                
            except Exception as e:
                await session.rollback()
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except:
                        pass
                raise e

    # Execute async database and ML flow in Celery's event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    return loop.run_until_complete(_async_process())
