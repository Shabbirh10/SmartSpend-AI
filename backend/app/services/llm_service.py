import ollama
import json

class LLMService:
    def __init__(self, model="llama3"):
        self.model = model

    def categorise_transaction(self, description, amount):
        """
        Uses Llama 3 to categorize a transaction.
        """
        try:
            prompt = f"""
            Categorize this transaction into one of: [Food, Transport, Shopping, Entertainment, Health, Bills, Travel, Groceries].
            Return ONLY the category name.
            
            Transaction: {description}
            Amount: {amount}
            """
            
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt},
            ])
            
            return response['message']['content'].strip()
        except Exception as e:
            print(f"Ollama Error: {e}")
            return None # Fallback to rule-based or ML model

    def parse_pdf_text(self, raw_text):
        """
        Extracts structured data from raw PDF text if Regex fails.
        """
        try:
            prompt = f"""
            Extract transaction data from this text. Return JSON array: [{{ "date": "DD/MM/YYYY", "description": "...", "amount": 0.00 }}]
            
            Text:
            {raw_text[:2000]}  # Limit token usage
            """
             
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt},
            ])
            
            content = response['message']['content']
            # Basic cleanup to find JSON brackets
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
            return []
        except Exception as e:
            print(f"Ollama Parse Error: {e}")
            return []

llm = LLMService()
