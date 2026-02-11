import pdfplumber
import re
from datetime import datetime

class PDFParser:
    def extract_transactions(self, pdf_path):
        """
        Extracts transactions from a PDF.
        Returns a list of dicts: {'date': str, 'description': str, 'amount': float}
        """
        transactions = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                # Basic line-by-line parsing (Example for generic statement)
                # This needs to be improved with Regex or LLMs for specific banks
                lines = text.split('\n')
                for line in lines:
                    # Look for date pattern (DD/MM/YYYY)
                    date_match = re.search(r'\d{2}/\d{2}/\d{4}', line)
                    # Look for amount pattern (1,234.56 or 1234.56)
                    amount_match = re.search(r'\d{1,3}(?:,\d{3})*(?:\.\d{2})', line)
                    
                    if date_match and amount_match:
                        try:
                            date_str = date_match.group(0)
                            amount_str = amount_match.group(0).replace(',', '')
                            
                            # Description is usually between date and amount
                            # This is a naive heuristic; LLM works better here
                            desc_start = date_match.end()
                            desc_end = amount_match.start()
                            description = line[desc_start:desc_end].strip()
                            
                            if description:
                                transactions.append({
                                    'date': datetime.strptime(date_str, '%d/%m/%Y').date(),
                                    'description': description,
                                    'amount': float(amount_str)
                                })
                        except Exception as e:
                            print(f"Skipping line: {line} - Error: {e}")
                            continue
                            
        return transactions

parser = PDFParser()
