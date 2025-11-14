# **CreditCardStatementAnalyser**

CreditCardStatementAnalyser is a Python project I built to automatically read, clean, and analyze credit card statements. Instead of going through transactions manually, this tool extracts useful insights such as spending categories, monthly totals, high-value transactions, and patterns in expenses.

---

## **About the Project**

I created this tool to make it easier to understand where money is going each month. Many banks export statements in messy formats (PDF/CSV), and manually going through transactions is time-consuming.
This project parses the data, organizes it, and gives a clear breakdown of spending.

---

## **What It Can Do**

* Read and process credit card statements
* Clean and format transaction data
* Categorize expenses (food, travel, shopping, utilities, etc.)
* Calculate total monthly spending
* Identify top categories and biggest transactions
* Generate summaries for quick insights
* Export cleaned data for further analysis

*(If yours also reads PDFs, let me know and I’ll update this section.)*

---

## **Tech Stack**

* **Python 3**
* **Pandas** (data cleaning & analysis)
* **NumPy**
* **matplotlib / seaborn** (optional for graphs)
* **tabula / pdfplumber** (if you're parsing PDFs)

---

## **Project Structure**

```
CreditCardStatementAnalyser/
│── data/                    # Sample statements
│── output/                  # Processed files & summaries
│── src/
│    ├── parser.py           # Reads and cleans statement data
│    ├── categorizer.py      # Categorizes transactions
│    ├── analyzer.py         # Generates insights
│    └── visualizer.py       # Optional charts
│── main.py                  # Entry point
│── requirements.txt
│── README.md
```

---

## **How to Use**

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Place your statement file in the `data/` folder.

3. Run the script:

```bash
python main.py
```

4. The cleaned transactions and summary will appear inside the `output/` folder.

---

## **Why I Built This**

I wanted a simple way to understand my spending without relying on complicated apps. This project helped me practice:

* Data cleaning
* Working with financial datasets
* Categorizing real transactions
* Python scripting and modular code design

---

## **Possible Future Improvements**

* Automatic PDF reading
* More advanced categorization using ML
* Monthly/Yearly dashboards
* A small GUI or web interface
* Export to Excel / Google Sheets

