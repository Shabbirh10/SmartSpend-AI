import re

class PIIScrubber:
    def __init__(self):
        # Define high-performance regex patterns for common PII
        self.patterns = {
            'EMAIL': re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'),
            'PHONE': re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            'SSN': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'CREDIT_CARD': re.compile(r'\b(?:\d[ -]*?){13,16}\b'),
            'IP_ADDRESS': re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
            'ACCOUNT_NUMBER': re.compile(r'\b\d{9,18}\b') # Standard banking account numbers
        }

    def scrub(self, text: str) -> str:
        if not text:
            return ""
        
        scrubbed = text
        for pii_type, regex in self.patterns.items():
            scrubbed = regex.sub(f"[SCRUBBED_{pii_type}]", scrubbed)
            
        return scrubbed

pii_scrubber = PIIScrubber()
