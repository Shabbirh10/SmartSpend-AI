import os
import json
from openai import OpenAI

class LLMService:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def _chat(self, system_prompt, user_prompt):
        """
        Sends a chat completion request to OpenAI.
        Returns the assistant's message content.
        """
        if not self.client:
            raise RuntimeError("OPENAI_API_KEY not set")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    def categorise_transaction(self, description, amount):
        """
        Uses OpenAI to categorize a transaction.
        """
        try:
            system_prompt = (
                "You are a transaction categorizer. "
                "Categorize the transaction into one of: "
                "[Food, Transport, Shopping, Entertainment, Health, Bills, Travel, Groceries]. "
                "Return ONLY the category name."
            )
            user_prompt = f"Transaction: {description}\nAmount: {amount}"
            return self._chat(system_prompt, user_prompt)
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return None  # Fallback to rule-based or ML model

    def chat(self, query, context=""):
        """
        Financial assistant chat powered by OpenAI.
        """
        try:
            system_prompt = (
                "You are a helpful financial assistant for SmartSpend AI. "
                "Answer the user's question based on their recent transactions. "
                "Be concise and helpful."
            )
            user_prompt = f"Recent transactions:\n{context}\n\nUser Question: {query}"
            return self._chat(system_prompt, user_prompt)
        except Exception as e:
            print(f"OpenAI Chat Error: {e}")
            return "AI is currently unavailable. Please check your API key configuration."

    def parse_pdf_text(self, raw_text):
        """
        Extracts structured data from raw PDF text if Regex fails.
        """
        try:
            system_prompt = (
                "You extract transaction data from bank statement text. "
                "Return a JSON array: "
                '[{ "date": "DD/MM/YYYY", "description": "...", "amount": 0.00 }]'
            )
            user_prompt = f"Text:\n{raw_text[:2000]}"
            content = self._chat(system_prompt, user_prompt)
            # Basic cleanup to find JSON brackets
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != 0:
                return json.loads(content[start:end])
            return []
        except Exception as e:
            print(f"OpenAI Parse Error: {e}")
            return []

llm = LLMService()
