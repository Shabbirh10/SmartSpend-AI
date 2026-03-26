import google.generativeai as genai
import json

genai.configure(api_key="AIzaSyAetw4WP48GW2pCtwCJASf00U2hqaWmJxQ")

class LLMService:
    def __init__(self, model="gemini-1.5-flash"):
        self.model_name = model

    def chat(self, prompt):
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini Error: {e}")
            return None

    def categorise_transaction(self, description, amount):
        """
        Uses Gemini to categorize a transaction.
        """
        prompt = f"""
        Categorize this transaction into one of: [Food, Transport, Shopping, Entertainment, Health, Bills, Travel, Groceries].
        Return ONLY the category name.
        
        Transaction: {description}
        Amount: {amount}
        """
        return self.chat(prompt)

    def parse_pdf_text(self, raw_text):
        """
        Extracts structured data from raw PDF text if Regex fails.
        """
        try:
            prompt = f"""
            Extract transaction data from this text. Return JSON array: [{{"date": "DD/MM/YYYY", "description": "...", "amount": 0.00}}]
            
            Text:
            {raw_text[:2000]}  # Limit token usage
            """
            content = self.chat(prompt)
            if not content:
                return []
            
            # Basic cleanup to find JSON brackets
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
            return []
        except Exception as e:
            print(f"Gemini Parse Error: {e}")
            return []

llm = LLMService()
