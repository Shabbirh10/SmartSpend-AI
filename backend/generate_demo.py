import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from datetime import datetime, timedelta
import random

def generate_realistic_bank_statement(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle(
        'BankTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#003049'),
        alignment=1, # Center
        spaceAfter=20
    )
    elements.append(Paragraph("SMART BANK OF INDIA", title_style))
    elements.append(Paragraph("Account Statement", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    # Account Details
    details = [
        ["Account Holder:", "Rohan Sharma"],
        ["Account Number:", "0000 1234 5678"],
        ["Statement Period:", "01-Jul-2025 to 30-Jun-2026"],
        ["Branch:", "Mumbai Central"]
    ]
    t_details = Table(details, colWidths=[120, 300])
    t_details.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_details)
    elements.append(Spacer(1, 24))
    
    # Transactions Table Header
    data = [["Date", "Description", "Ref No", "Debit (INR)", "Credit (INR)", "Balance (INR)"]]
    
    # Transactions
    merchants = [
        ("Zomato Ltd", 350, 800),
        ("Swiggy", 250, 600),
        ("Uber India", 150, 450),
        ("Amazon India", 500, 2500),
        ("Flipkart", 800, 3000),
        ("Jio Prepaid", 299, 299),
        ("Blinkit", 400, 900),
        ("BigBasket", 1200, 1500),
        ("BookMyShow", 500, 800),
        ("Indian Oil", 1000, 2000),
        ("Starbucks", 300, 500),
        ("Dmart", 2000, 4000),
        ("Apollo Pharmacy", 150, 400),
        ("Netfix Subscription", 499, 499)
    ]
    
    balance = 120500.00 # Starting balance
    current_date = datetime(2025, 7, 1)
    end_date = datetime(2026, 6, 30)
    
    current_month = current_date.month
    
    while current_date <= end_date:
        # Check if month changed to add salary
        if current_date.month != current_month:
            balance += 85000
            data.append([
                current_date.replace(day=1).strftime("%d/%m/%Y"),
                "NEFT * SALARY * TECH CORP",
                f"N{random.randint(100000, 999999)}",
                "",
                "85000.00",
                f"{balance:.2f}"
            ])
            current_month = current_date.month

        # Generate a random transaction 3-4 times a week on average
        if random.random() < 0.5:
            merchant, min_amt, max_amt = random.choice(merchants)
            amt = float(random.randint(min_amt, max_amt))
            
            balance -= amt
            data.append([
                current_date.strftime("%d/%m/%Y"),
                f"{merchant}",
                f"REF{random.randint(10000, 99999)}",
                f"{amt:.2f}",
                "",
                f"{balance:.2f}"
            ])
        
        current_date += timedelta(days=1)
        
    # Add final salary if missed at the exact end
    if current_date.day > 1 and current_month != end_date.month:
        balance += 85000
        data.append([
            end_date.replace(day=1).strftime("%d/%m/%Y"),
            "NEFT * SALARY * TECH CORP",
            f"N{random.randint(100000, 999999)}",
            "",
            "85000.00",
            f"{balance:.2f}"
        ])
        
    # Table Style
    t = Table(data, colWidths=[70, 200, 60, 70, 70, 80], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003049')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (3,0), (-1,-1), 'RIGHT'), # Align amounts right
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#fdf0d5')),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#003049')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#003049')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f7f7f7')])
    ]))
    
    elements.append(t)
    
    # Disclaimer
    elements.append(Spacer(1, 30))
    disclaimer = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7,
        textColor=colors.gray
    )
    elements.append(Paragraph("This is a computer generated statement and does not require a signature.", disclaimer))
    
    doc.build(elements)
    print(f"Generated {filename}")

if __name__ == '__main__':
    generate_realistic_bank_statement('/Users/shabbirhardwarewala/Desktop/Projects/smartspend/demo_statement.pdf')
