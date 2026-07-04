import pytest
import json
from unittest.mock import patch

def test_health_check(client):
    res = client.get('/health')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'smartspend-ai-backend'

def test_get_transactions_empty(client):
    res = client.get('/api/transactions')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert 'data' in data
    assert len(data['data']) == 0
    assert 'pagination' in data
    assert data['pagination']['total'] == 0

def test_get_trends_empty(client):
    res = client.get('/api/analytics/trends')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert 'data' in data
    assert len(data['data']) == 0

def test_get_subscriptions_empty(client):
    res = client.get('/api/analytics/subscriptions')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert 'data' in data
    assert len(data['data']) == 0

@patch("app.services.agent_service.finance_agent.chat_stream")
def test_chat_route(mock_chat, client):
    # Mocking Gemini response stream
    mock_chat.return_value = ["This is a mock response."]
    
    res = client.post('/api/chat', json={"query": "How much did I spend?"})
    assert res.status_code == 200
    data = json.loads(res.data)
    assert "response" in data
    assert data["response"] == "This is a mock response."

@patch("app.services.agent_service.finance_agent.chat_stream")
def test_chat_stream_route(mock_chat, client):
    # Mocking Gemini response stream
    mock_chat.return_value = ["Hello ", "world!"]
    
    res = client.post('/api/chat/stream', json={"query": "Analyze my statement."})
    assert res.status_code == 200
    assert res.mimetype == "text/event-stream"
    
    # Parse event stream output
    body = res.data.decode('utf-8')
    assert "Hello" in body
    assert "world!" in body
