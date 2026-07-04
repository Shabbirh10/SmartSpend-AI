import sqlite3
import random

tickers = [
    "CSCO", "QCOM", "TXN", "AVGO",
    "JPM", "BAC", "WFC", "C", "GS", "MS", "V", "MA", "AXP", "PYPL",
    "JNJ", "PFE", "MRK", "ABT", "TMO", "UNH", "CVS", "CI", "HUM", "MDT",
    "WMT", "TGT", "COST", "HD", "LOW", "MCD", "SBUX", "NKE", "DIS", "KO",
    "PEP", "PG", "CL", "KMB", "GIS", "K", "MDLZ", "HSY", "TSN", "HRL"
]

conn = sqlite3.connect('smartspend.db')
cursor = conn.cursor()

for ticker in tickers:
    shares = round(random.uniform(5.0, 100.0), 2)
    price = round(random.uniform(20.0, 300.0), 2)
    try:
        cursor.execute("INSERT INTO investment (ticker, shares, average_price) VALUES (?, ?, ?)", (ticker, shares, price))
        print(f"Added {ticker}")
    except Exception as e:
        print(f"Skipped {ticker}: {e}")

conn.commit()
conn.close()
