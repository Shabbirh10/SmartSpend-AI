import os
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from app.services.parser import parser
from app.services.classifier import classifier
from app.models import db, Statement, Transaction
from datetime import datetime

api_bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/upload', methods=['POST'])
def upload_statement():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Save file temporarily
        upload_folder = os.path.join(current_app.root_path, '../uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        try:
            # 1. Parse PDF
            raw_transactions = parser.extract_transactions(filepath)
            
            # 2. Save Statement Metadata
            statement = Statement(filename=filename, bank_name="Unknown")
            db.session.add(statement)
            db.session.flush() # Get ID
            
            analyzed_data = []
            
            # 3. Categorize and Save Transactions
            for item in raw_transactions:
                category = classifier.predict(item['description'])
                
                # Check for anomaly (simple rule-based for now, e.g., > $1000)
                is_anomaly = item['amount'] > 1000.0
                
                txn = Transaction(
                    statement_id=statement.id,
                    date=item['date'],
                    description=item['description'],
                    amount=item['amount'],
                    category=category,
                    is_anomaly=is_anomaly
                )
                db.session.add(txn)
                
                item['category'] = category
                item['is_anomaly'] = is_anomaly
                item['date'] = item['date'].isoformat() # Serialize date
                analyzed_data.append(item)
            
            db.session.commit()
            
            # Cleanup
            os.remove(filepath)
            
            return jsonify({
                'message': 'File processed successfully',
                'statement_id': statement.id,
                'transactions': analyzed_data
            }), 201
            
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400

@api_bp.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return jsonify({'data': [t.to_dict() for t in transactions]}), 200

@api_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # 1. Fetch recent context (simplest RAG)
    recent_txns = Transaction.query.order_by(Transaction.date.desc()).limit(10).all()
    context = "\n".join([f"{t.date}: {t.description} - ${t.amount} ({t.category})" for t in recent_txns])
    
    # 2. Construct Prompt for Ollama
    try:
        from app.services.llm_service import llm
        prompt = f"""
        You are a financial assistant. Answer the user's question based on these recent transactions:
        {context}
        
        User Question: {query}
        """
        response = llm.categorise_transaction(query, 0) # Abusing categorise for chat to save lines or make a new method
        # Ideally, LLMService should have a 'chat' method. Let's assume we update LLMService or use 'ollama.chat' directly here.
        # But for 'code correctness', let's use the actual library here or update LLMService.
        # Let's use ollama directly here for simplicity if LLMService isn't perfect.
        import ollama
        res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
        return jsonify({'response': res['message']['content']})
    except Exception as e:
        return jsonify({'response': "AI is currently offline (Ollama not running).", 'error': str(e)})

@api_bp.route('/analytics/trends', methods=['GET'])
def get_trends():
    transactions = Transaction.query.all()
    trend_data = {}
    
    for t in transactions:
        month_key = t.date.strftime("%Y-%m")
        trend_data[month_key] = trend_data.get(month_key, 0) + t.amount
        
    sorted_trends = [{"date": k, "amount": v} for k, v in sorted(trend_data.items())]
    return jsonify({'data': sorted_trends})

@api_bp.route('/analytics/subscriptions', methods=['GET'])
def get_subscriptions():
    from collections import Counter
    transactions = Transaction.query.all()
    
    desc_counts = Counter([t.description for t in transactions])
    subscriptions = []
    
    processed = set()
    for t in transactions:
        if desc_counts[t.description] > 1 and t.description not in processed:
            subscriptions.append({
                "name": t.description,
                "amount": t.amount,
                "frequency": "Monthly"
            })
            processed.add(t.description)
            
    return jsonify({'data': subscriptions})

@api_bp.route('/demo/download', methods=['GET'])
def download_demo():
    import os
    from flask import send_file
    
    demo_path = os.path.abspath(os.path.join(current_app.root_path, '../../demo_statement.pdf'))
    
    if not os.path.exists(demo_path):
        return jsonify({'error': 'Demo file not generated yet'}), 404
        
    return send_file(demo_path, as_attachment=True, download_name='demo_statement.pdf')

