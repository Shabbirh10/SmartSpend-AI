import sqlite3
import os
import json
from datetime import datetime
import google.generativeai as genai

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../instance/smartspend.db'))

def execute_query(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        conn.close()

# Define the tools for Gemini Function Calling
def list_recent_transactions(limit: int = 10) -> str:
    """
    Retrieves the most recent transactions from the database.

    Args:
        limit: The maximum number of transactions to retrieve. Defaults to 10.
    """
    sql = 'SELECT date, description, amount, category, is_anomaly FROM "transaction" ORDER BY date DESC LIMIT ?'
    results = execute_query(sql, (limit,))
    return json.dumps(results)

def search_transactions(query_str: str = None, category: str = None, min_amount: float = None, max_amount: float = None, start_date: str = None, end_date: str = None) -> str:
    """
    Searches and filters transactions by matching description query, category, amount, or date ranges.

    Args:
        query_str: Text search matching transaction description.
        category: Exact match category name.
        min_amount: Filter transactions with amount >= min_amount.
        max_amount: Filter transactions with amount <= max_amount.
        start_date: Start date string (YYYY-MM-DD).
        end_date: End date string (YYYY-MM-DD).
    """
    conditions = []
    params = []
    if query_str:
        conditions.append("description LIKE ?")
        params.append(f"%{query_str}%")
    if category:
        conditions.append("category = ?")
        params.append(category)
    if min_amount is not None:
        conditions.append("amount >= ?")
        params.append(min_amount)
    if max_amount is not None:
        conditions.append("amount <= ?")
        params.append(max_amount)
    if start_date:
        conditions.append("date >= ?")
        params.append(start_date)
    if end_date:
        conditions.append("date <= ?")
        params.append(end_date)
        
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    sql = f'SELECT date, description, amount, category, is_anomaly FROM "transaction"{where_clause} ORDER BY date DESC LIMIT 50'
    results = execute_query(sql, params)
    return json.dumps(results)

def compute_spend_statistics(category: str = None, start_date: str = None, end_date: str = None) -> str:
    """
    Computes aggregate metrics (total spend, average transaction amount, count of transactions, min, and max spend) for a category or overall.

    Args:
        category: Optional category name to restrict analysis.
        start_date: Optional start date string (YYYY-MM-DD).
        end_date: Optional end date string (YYYY-MM-DD).
    """
    conditions = []
    params = []
    if category:
        conditions.append("category = ?")
        params.append(category)
    if start_date:
        conditions.append("date >= ?")
        params.append(start_date)
    if end_date:
        conditions.append("date <= ?")
        params.append(end_date)
        
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    sql = f'SELECT COUNT(*) as count, SUM(amount) as total, AVG(amount) as average, MIN(amount) as min, MAX(amount) as max FROM "transaction"{where_clause}'
    results = execute_query(sql, params)
    return json.dumps(results[0] if results else {})


class FinanceAgent:
    def __init__(self, model="gemini-2.5-flash"):
        api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyAetw4WP48GW2pCtwCJASf00U2hqaWmJxQ")
        genai.configure(api_key=api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=[list_recent_transactions, search_transactions, compute_spend_statistics],
            system_instruction=(
                "You are SmartSpend AI, an intelligent, conversational financial assistant.\n"
                "You help users inspect their statement uploads, track subscriptions, analyze trends, and identify anomalies.\n"
                "You MUST use your database tools whenever you need to fetch transactions, filter by dates, compute aggregate metrics, or perform searches.\n"
                "Never invent financial data. If no transactions are found, tell the user honestly.\n"
                "Always format currency as $XX.XX. Keep responses concise, friendly, and structured."
            )
        )

    def chat_stream(self, query):
        """
        Executes a ReAct chat loop with Gemini and yields final response text in real-time.
        """
        chat = self.model.start_chat()
        # Initial call - using send_message with stream=True
        response_stream = chat.send_message(query, stream=True)
        
        while True:
            # Consume stream to check for function calls
            chunks = list(response_stream)
            first_part = None
            if chunks and chunks[0].candidates:
                first_part = chunks[0].candidates[0].content.parts[0]
            
            if first_part and first_part.function_call:
                # Gather all function calls
                tool_parts = []
                for chunk in chunks:
                    if chunk.candidates:
                        for part in chunk.candidates[0].content.parts:
                            if part.function_call:
                                tool_parts.append(part.function_call)
                
                tool_responses = []
                for call in tool_parts:
                    name = call.name
                    args = dict(call.args)
                    
                    if name == "list_recent_transactions":
                        res_str = list_recent_transactions(**args)
                    elif name == "search_transactions":
                        res_str = search_transactions(**args)
                    elif name == "compute_spend_statistics":
                        res_str = compute_spend_statistics(**args)
                    else:
                        res_str = json.dumps({"error": f"Unknown tool: {name}"})
                        
                    tool_responses.append(
                        {
                            "function_response": {
                                "name": name,
                                "response": {"result": res_str}
                            }
                        }
                    )
                
                # Send tool responses back using send_message with stream=True
                response_stream = chat.send_message(tool_responses, stream=True)
            else:
                # Direct conversational text, yield it!
                for chunk in chunks:
                    if chunk.candidates and chunk.candidates[0].content.parts:
                        for part in chunk.candidates[0].content.parts:
                            if part.text:
                                yield part.text
                break

finance_agent = FinanceAgent()
