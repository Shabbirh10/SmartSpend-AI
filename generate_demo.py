from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
import random

def generate_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    def draw_header(c, page_bum):
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Bank of AI - Platinum Rewards Statement")
        c.setFont("Helvetica", 10)
        c.drawString(450, height - 50, f"Page {page_bum} of 3")
        c.drawString(50, height - 70, f"Statement Period: {datetime.now().strftime('%B %Y')}")
        c.drawString(50, height - 85, "Account Number: **** **** **** 8842")
        c.line(50, height - 95, 550, height - 95)
        
        # Table Header
        y = height - 120
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, y, "Trans Date")
        c.drawString(110, y, "Post Date")
        c.drawString(180, y, "Description")
        c.drawString(480, y, "Amount ($)")
        c.line(50, y-5, 550, y-5)
        return y - 25

    y = draw_header(c, 1)
    
    # Complex Seed Data
    merchants = [
        ("UBER *TRIP 8485", "Transport", 15, 45),
        ("UBER EATS San Francisco", "Food", 20, 60),
        ("AMZN Mktp US*1A2B3C", "Shopping", 10, 150),
        ("NETFLIX.COM", "Entertainment", 15.99, 15.99),
        ("SPOTIFY USA", "Entertainment", 11.99, 11.99),
        ("STARBUCKS STORE #19202", "Food", 4, 12),
        ("SHELL OIL 57382", "Transport", 35, 70),
        ("TRADER JOE'S #502", "Groceries", 40, 120),
        ("WHOLE FOODS MARKET", "Groceries", 50, 200),
        ("APPLE.COM/BILL", "Shopping", 0.99, 29.99),
        ("DOORDASH*CHIPOTLE", "Food", 15, 40),
        ("LYFT *RIDE PHOENIX", "Transport", 12, 35),
        ("CVS PHARMACY #9382", "Health", 8, 45),
        ("TARGET t-2832", "Shopping", 25, 100),
        ("Introduction to AI Course", "Education", 49, 199),
        ("GITHUB *PRO SUBSCRIPTION", "Tech", 10, 10),
        ("OPENAI *CHATGPT PLUS", "Tech", 20, 20),
        ("DIGITALOCEAN *CLOUD", "Tech", 15, 50),
        ("AWS EMEA *SERVICE", "Tech", 30, 100),
        ("DELTA AIR LINES 00623", "Travel", 150, 600),
        ("AIRBNB *HM28392", "Travel", 100, 400),
        ("HOTEL TONIGHT", "Travel", 120, 300),
        ("AMC THEATRES", "Entertainment", 20, 50),
        ("PLAYSTATION NETWORK", "Entertainment", 10, 70)
    ]

    transactions = []
    start_date = datetime.now() - timedelta(days=60)
    
    # Generate 75 random transactions
    for _ in range(75):
        m = random.choice(merchants)
        desc = m[0]
        amt = round(random.uniform(m[2], m[3]), 2)
        
        # Random date logic
        days_offset = random.randint(0, 60)
        t_date = start_date + timedelta(days=days_offset)
        p_date = t_date + timedelta(days=random.randint(0, 3)) # Post date is later
        
        transactions.append({
            "t_date": t_date,
            "p_date": p_date,
            "desc": desc,
            "amt": amt
        })
        
    # Sort by date
    transactions.sort(key=lambda x: x['t_date'])
    
    # Add noise / anomalies
    transactions.insert(10, {"t_date": start_date + timedelta(days=5), "p_date": start_date + timedelta(days=6), "desc": "PAYMENT - THANK YOU", "amt": -1500.00})
    transactions.insert(40, {"t_date": start_date + timedelta(days=35), "p_date": start_date + timedelta(days=35), "desc": "INTEREST CHARGE - PURCHASES", "amt": 24.50})
    transactions.append({"t_date": datetime.now(), "p_date": datetime.now(), "desc": "APPLE STORE #T382 (High Value)", "amt": 2499.00}) # Anomaly
    
    page = 1
    for t in transactions:
        if y < 50:
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(50, 30, "Continued on next page...")
            c.showPage()
            page += 1
            y = draw_header(c, page)
            c.setFont("Helvetica", 10)
            
        c.drawString(50, y, t['t_date'].strftime("%d/%m/%Y"))
        c.drawString(110, y, t['p_date'].strftime("%d/%m"))
        c.drawString(180, y, t['desc'])
        
        # Right align amount
        amt_str = f"{t['amt']:.2f}"
        if t['amt'] < 0:
            amt_str = f"{t['amt']:.2f}".replace("-", "") + " CR"
            
        c.drawRightString(540, y, amt_str)
        y -= 15

    # Footer
    c.line(50, y-10, 550, y-10)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y-25, "Total New Balance: $1,284.32")
    c.drawString(350, y-25, "Minimum Payment Due: $35.00")

    c.save()
    print(f"Generated complex {filename} with ({len(transactions)} transactions)")

if __name__ == "__main__":
    generate_pdf("demo_statement.pdf")
