import os
import json
import hashlib
from flask import Blueprint, jsonify, request, current_app, Response
from werkzeug.utils import secure_filename
from app.models import async_session, Statement, Transaction
from app import limiter, cache
from celery.result import AsyncResult
from sqlalchemy import select, func

api_bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")
def upload_statement():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Save file to uploads directory
        upload_folder = os.path.join(current_app.root_path, '../uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Trigger Celery background task
        from app.tasks import process_statement_task
        task = process_statement_task.delay(filepath, filename)
        
        return jsonify({
            'message': 'File upload successful. Processing started in background.',
            'task_id': task.id
        }), 202

    return jsonify({'error': 'Invalid file type'}), 400

@api_bp.route('/tasks/<task_id>', methods=['GET'])
@limiter.limit("120 per minute")
def get_task_status(task_id):
    celery_app = current_app.extensions['celery']
    res = AsyncResult(task_id, app=celery_app)
    
    if res.state == 'PENDING':
        return jsonify({
            'state': res.state,
            'status': 'Pending...'
        }), 200
    elif res.state == 'SUCCESS':
        # Invalidate analytics cache upon successful processing
        cache.delete("analytics_trends")
        cache.delete("analytics_subscriptions")
        return jsonify({
            'state': res.state,
            'result': res.result
        }), 200
    elif res.state == 'FAILURE':
        return jsonify({
            'state': res.state,
            'status': 'Task failed during execution',
            'error': str(res.info)
        }), 500
    else:
        return jsonify({
            'state': res.state,
            'status': 'Processing...'
        }), 200

@api_bp.route('/transactions', methods=['GET'])
@limiter.limit("60 per minute")
async def get_transactions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 100)  # Cap at 100

    # Async query using async_sessionmaker
    async with async_session() as session:
        total_stmt = select(func.count()).select_from(Transaction)
        total = (await session.execute(total_stmt)).scalar()
        
        stmt = select(Transaction).order_by(Transaction.date.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await session.execute(stmt)
        transactions = result.scalars().all()

    return jsonify({
        'data': [t.to_dict() for t in transactions],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 1
        }
    }), 200

@api_bp.route('/chat', methods=['POST'])
@limiter.limit("30 per minute")
def chat():
    # Deprecated fallback/direct chat endpoint, redirects to streaming
    data = request.json or {}
    query = data.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
        
    from app.services.pii_scrubber import pii_scrubber
    scrubbed_query = pii_scrubber.scrub(query)
    
    # Cache lookup
    query_hash = hashlib.md5(scrubbed_query.encode('utf-8')).hexdigest()
    cache_key = f"chat_response_{query_hash}"
    cached_res = cache.get(cache_key)
    if cached_res:
        return jsonify({'response': cached_res})
        
    try:
        from app.services.agent_service import finance_agent
        # Consume the stream synchronously for this fallback
        res_list = list(finance_agent.chat_stream(scrubbed_query))
        res = "".join(res_list)
        if res:
            cache.set(cache_key, res, timeout=600)
            return jsonify({'response': res})
        return jsonify({'response': "AI is currently offline.", 'error': "Failed to generate response"})
    except Exception as e:
        return jsonify({'response': "AI is currently offline.", 'error': str(e)})

@api_bp.route('/chat/stream', methods=['POST'])
@limiter.limit("30 per minute")
def chat_stream():
    data = request.json or {}
    query = data.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
        
    from app.services.pii_scrubber import pii_scrubber
    scrubbed_query = pii_scrubber.scrub(query)
    
    # Hash query for cache check
    query_hash = hashlib.md5(scrubbed_query.encode('utf-8')).hexdigest()
    cache_key = f"chat_response_{query_hash}"
    
    cached_response = cache.get(cache_key)
    if cached_response:
        def generate_cached():
            # Send word by word to emulate real-time stream
            words = cached_response.split(" ")
            for i in range(0, len(words), 3):
                chunk = " ".join(words[i:i+3]) + " "
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        return Response(generate_cached(), mimetype='text/event-stream')

    from app.services.agent_service import finance_agent
    
    def generate():
        full_response = []
        try:
            for chunk in finance_agent.chat_stream(scrubbed_query):
                full_response.append(chunk)
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Cache full response on completion
            cache.set(cache_key, "".join(full_response), timeout=600)
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
    return Response(generate(), mimetype='text/event-stream')

@api_bp.route('/analytics/trends', methods=['GET'])
@limiter.limit("60 per minute")
async def get_trends():
    # Cache lookup
    cached_trends = cache.get("analytics_trends")
    if cached_trends:
        return jsonify(cached_trends), 200

    async with async_session() as session:
        stmt = select(Transaction)
        result = await session.execute(stmt)
        transactions = result.scalars().all()
    
    trend_data = {}
    for t in transactions:
        month_key = t.date.strftime("%Y-%m")
        trend_data[month_key] = trend_data.get(month_key, 0) + t.amount
        
    sorted_trends = [{"date": k, "amount": v} for k, v in sorted(trend_data.items())]
    response_data = {'data': sorted_trends}
    
    # Cache result
    cache.set("analytics_trends", response_data, timeout=300)
    return jsonify(response_data), 200

@api_bp.route('/analytics/categories', methods=['GET'])
@limiter.limit("60 per minute")
async def get_categories():
    cached = cache.get("analytics_categories")
    if cached:
        return jsonify(cached), 200

    async with async_session() as session:
        stmt = (
            select(
                Transaction.category,
                func.sum(Transaction.amount).label("total")
            )
            .group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount).desc())
        )
        result = await session.execute(stmt)
        rows = result.all()

    data = [{"name": row.category, "value": round(float(row.total), 2)} for row in rows if row.category and row.total > 0]
    response = {"data": data}
    cache.set("analytics_categories", response, timeout=120)
    return jsonify(response), 200

@api_bp.route('/analytics/subscriptions', methods=['GET'])
@limiter.limit("60 per minute")
async def get_subscriptions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)
    per_page = min(per_page, 100)

    # Cache lookup
    cache_key = f"analytics_subs_{page}_{per_page}"
    cached_subs = cache.get(cache_key)
    if cached_subs:
        return jsonify(cached_subs), 200

    # Known subscription service keywords mapped to clean display names
    SUBSCRIPTION_KEYWORDS = {
        "netflix": "Netflix",
        "netfix": "Netflix",
        "spotify": "Spotify",
        "amazon prime": "Amazon Prime",
        "hotstar": "Disney+ Hotstar",
        "zee5": "ZEE5",
        "sony liv": "SonyLIV",
        "sonyliv": "SonyLIV",
        "jio": "Jio",
        "airtel": "Airtel",
        "bsnl": "BSNL",
        "youtube premium": "YouTube Premium",
        "youtube": "YouTube Premium",
        "apple": "Apple Subscription",
        "microsoft": "Microsoft 365",
        "google one": "Google One",
        "linkedin": "LinkedIn Premium",
        "gym": "Gym Membership",
        "fitness": "Fitness Membership",
        "prime video": "Amazon Prime Video",
        "adobe": "Adobe Creative Cloud",
        "swiggy one": "Swiggy One",
        "zomato pro": "Zomato Pro",
        "zomato gold": "Zomato Gold",
    }

    async with async_session() as session:
        stmt = (
            select(
                Transaction.description,
                func.avg(Transaction.amount).label("avg_amount"),
                func.count(Transaction.id).label("occurrences")
            )
            .group_by(Transaction.description)
            .having(func.count(Transaction.id) > 1)
            .order_by(func.count(Transaction.id).desc())
        )
        result = await session.execute(stmt)
        rows = result.all()

    subscriptions = []
    seen_names = set()
    for row in rows:
        desc_lower = row.description.lower()
        matched_name = None
        for keyword, clean_name in SUBSCRIPTION_KEYWORDS.items():
            if keyword in desc_lower:
                matched_name = clean_name
                break
        if matched_name and matched_name not in seen_names:
            seen_names.add(matched_name)
            subscriptions.append({
                "name": matched_name,
                "amount": round(float(row.avg_amount), 2),
                "frequency": "Monthly" if row.occurrences <= 13 else "Weekly"
            })

    total = len(subscriptions)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    start = (page - 1) * per_page
    end = start + per_page
    paginated = subscriptions[start:end]

    response_data = {
        'data': paginated,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages
        }
    }
    
    cache.set(cache_key, response_data, timeout=300)
    return jsonify(response_data), 200

@api_bp.route('/demo/download', methods=['GET'])
@limiter.limit("30 per minute")
def download_demo():
    from flask import send_file
    demo_path = os.path.abspath(os.path.join(current_app.root_path, '../../demo_statement.pdf'))
    
    if not os.path.exists(demo_path):
        return jsonify({'error': 'Demo file not generated yet'}), 404
        
    return send_file(demo_path, as_attachment=True, download_name='demo_statement.pdf')

@api_bp.route('/portfolio', methods=['GET'])
@limiter.limit("30 per minute")
async def get_portfolio():
    from app.services.portfolio_service import get_portfolio_summary
    data = await get_portfolio_summary()
    return jsonify(data), 200

@api_bp.route('/portfolio/add', methods=['POST'])
@limiter.limit("10 per minute")
async def api_add_investment():
    data = request.json
    ticker = data.get('ticker')
    shares = data.get('shares')
    price = data.get('price')

    if not all([ticker, shares, price]):
        return jsonify({'error': 'Missing required fields: ticker, shares, price'}), 400

    from app.services.portfolio_service import add_investment
    try:
        inv = await add_investment(ticker, float(shares), float(price))
        return jsonify({'message': 'Investment added', 'investment': inv}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/portfolio/history', methods=['GET'])
@limiter.limit("30 per minute")
async def get_portfolio_history():
    ticker = request.args.get('ticker', 'SPY')
    
    cache_key = f"ticker_history_{ticker}"
    cached_history = cache.get(cache_key)
    if cached_history:
        return jsonify(cached_history), 200

    import yfinance as yf
    try:
        data = yf.download(ticker, period="1y", interval="1d", progress=False)
        history = []
        for date, row in data.iterrows():
            if not isinstance(row['Close'], (int, float)):
                close_val = float(row['Close'].iloc[0]) if hasattr(row['Close'], 'iloc') else float(row['Close'])
            else:
                close_val = float(row['Close'])
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "amount": close_val
            })
        
        response_data = {'data': history, 'ticker': ticker}
        cache.set(cache_key, response_data, timeout=3600)
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/news', methods=['GET'])
@limiter.limit("30 per minute")
async def get_indian_financial_news():
    cache_key = "indian_financial_news_v2"
    cached_news = cache.get(cache_key)
    if cached_news:
        return jsonify(cached_news), 200

    import urllib.request
    import xml.etree.ElementTree as ET
    
    try:
        url = "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        news_items = []
        for item in root.findall('./channel/item')[:10]:
            title = item.find('title').text if item.find('title') is not None else "No Title"
            link = item.find('link').text if item.find('link') is not None else "#"
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
            
            news_items.append({
                'title': title,
                'link': link,
                'pubDate': pub_date
            })
            
        response_data = {'data': news_items}
        cache.set(cache_key, response_data, timeout=1800) # Cache for 30 mins
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

