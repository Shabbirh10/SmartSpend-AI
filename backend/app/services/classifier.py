import re

CATEGORY_RULES = {
    "Food": [
        "zomato", "swiggy", "mcdonalds", "mcdonald", "kfc", "dominos", "pizza hut",
        "burger king", "subway", "starbucks", "cafe coffee day", "haldirams", "barbeque",
        "box8", "faasos", "biryani", "behrouz", "licious", "freshmenu", "eatfit",
        "rebel foods", "uber eats", "doordash", "uber eat", "food", "restaurant",
        "dining", "cafe", "bakery", "dhaba",
    ],
    "Transport": [
        "uber", "ola", "rapido", "metro card", "best bus", "irctc", "redbus",
        "indian railways", "railway", "indian oil", "bharat petroleum", "hpcl", "bpcl",
        "petrol", "fuel", "exxon", "shell", "lyft", "cab", "taxi", "auto",
        "parking", "fastag", "toll",
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "meesho", "snapdeal", "nykaa fashion",
        "ajio", "tata cliq", "reliance digital", "croma", "vijay sales", "lenskart",
        "ebay", "paypal", "lululemon", "ikea", "h&m", "zara", "best buy", "target",
        "walmart", "apple store", "nike", "adidas",
    ],
    "Groceries": [
        "bigbasket", "grofers", "jiomart", "blinkit", "zepto", "dmart", "d-mart",
        "more supermarket", "nature's basket", "milk basket", "country delight",
        "kroger", "trader joe", "whole foods", "safeway",
    ],
    "Entertainment": [
        "netflix", "netfix", "hotstar", "disney", "prime video", "sonyliv", "zee5",
        "mx player", "voot", "altbalaji", "jiocinema", "aha", "eros now", "bookmyshow",
        "pvr", "inox", "spotify", "youtube premium", "gaana", "jiosaavn", "wynk",
        "steam", "cinema", "movie", "theatre", "concert", "gaming",
    ],
    "Utilities": [
        "jio", "airtel", "bsnl", "vodafone", "vi mobile", "mseb", "bescom",
        "tata power", "adani electricity", "cesc", "bwssb", "mahanagar gas",
        "broadband", "act fibernet", "hathway", "electricity", "water bill",
        "gas bill", "recharge", "prepaid",
    ],
    "Health": [
        "apollo pharmacy", "medplus", "netmeds", "1mg", "pharmeasy", "practo",
        "doctor", "hospital", "clinic", "fortis", "max hospital", "manipal",
        "pharmacy", "medicine", "medical", "health", "co-pay", "insurance",
        "diagnostic", "lab test",
    ],
    "Investment": [
        "hdfc mutual", "sbi mutual", "zerodha", "groww", "paytm money", "upstox",
        "angel broking", "icici direct", "kotak securities", "mutual fund",
        "stock", "shares", "nse", "bse", "demat",
    ],
    "Beauty": [
        "nykaa", "purplle", "sugar cosmetics", "mamaearth", "wow skin", "lakme",
        "l'oreal", "himalaya", "forest essentials", "kama ayurveda", "lotus herbals",
        "plum", "mcaffeine", "minimalist", "dot and key", "derma co", "re'equil",
        "biotique", "salon", "saloon", "haircut", "spa", "beauty parlour",
    ],
    "Travel": [
        "makemytrip", "yatra", "goibibo", "ixigo", "easemytrip", "oyo", "fabhotel",
        "treebo", "airbnb", "indigo", "air india", "spicejet", "vistara", "go first",
        "hotel", "resort", "flight", "airline", "travel", "booking",
    ],
    "Income": [
        "salary", "neft", "credited", "imps credit", "freelance", "dividend",
        "interest credited", "tech corp", "employer",
    ],
}

class TransactionClassifier:
    def predict(self, description: str) -> str:
        desc = description.lower()
        for category, keywords in CATEGORY_RULES.items():
            for kw in keywords:
                if kw in desc:
                    return category
        return "Other"

classifier = TransactionClassifier()

