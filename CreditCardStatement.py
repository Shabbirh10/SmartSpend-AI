import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pdfplumber
import re

# ---------------------- Core Parser ----------------------
def extract_data_from_pdf(pdf_path):
    data = {
        "Card Issuer": "Unknown",
        "Card Last 4 Digits": "Not Found",
        "Billing Period": "Not Found",
        "Payment Due Date": "Not Found",
        "Total Amount Due": "Not Found"
    }

    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""

    text_upper = text.upper()

    # Detect issuer
    if "HDFC" in text_upper:
        data["Card Issuer"] = "HDFC Bank"
    elif "ICICI" in text_upper:
        data["Card Issuer"] = "ICICI Bank"
    elif "SBI" in text_upper:
        data["Card Issuer"] = "SBI Card"
    elif "AXIS" in text_upper:
        data["Card Issuer"] = "Axis Bank"
    elif "AMERICAN EXPRESS" in text_upper or "AMEX" in text_upper:
        data["Card Issuer"] = "American Express"

    # Extract Card Last 4 Digits
    last4 = re.search(r'(\d{4})(?!\d)', text)
    if last4:
        data["Card Last 4 Digits"] = last4.group(1)

    # Extract Payment Due Date
    due = re.search(r'Payment Due Date[:\s]+([0-9A-Za-z\-\/]+)', text)
    if due:
        data["Payment Due Date"] = due.group(1)

    # Extract Total Amount Due
    total_due = re.search(r'(?:Total (?:Amount )?Due|Amount Payable)[^\d]*(\d+[,\d]*\.\d{2})', text)
    if total_due:
        data["Total Amount Due"] = total_due.group(1)

    # Extract Billing Period (supports "Billing Period" or "Statement Period")
    bill_period = re.search(
    r'(?:Billing Period|Statement Period)[:\s]*'       # Label
    r'([0-9]{1,2}[-/][A-Za-z]{3,9}[-/]?[0-9]{2,4})'   # Start date
    r'\s*(?:to|TO|-)\s*'                               # Separator
    r'([0-9]{1,2}[-/][A-Za-z]{3,9}[-/]?[0-9]{2,4})',  # End date
    text
    )
    if bill_period:
        data["Billing Period"] = f"{bill_period.group(1)} to {bill_period.group(2)}"

        return data

# ---------------------- GUI ----------------------
class CreditCardParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💳 Credit Card Statement Parser")
        self.root.geometry("720x600")
        self.root.config(bg="#F9D895")

        # --- Title Bar ---
        title_frame = tk.Frame(root, bg="#27374D", pady=15)
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="💳 CREDIT CARD STATEMENT PARSER - SURE FINANCIAL",
                 fg="white", bg="#27374D", font=("Segoe UI", 18, "bold")).pack()

        # --- Supported Banks ---
        bank_frame = tk.Frame(root, bg="#F9D895", pady=10)
        bank_frame.pack(fill="x")

        tk.Label(bank_frame, text="Supported Banks:",
                 bg="#F9D895", fg="#27374D", font=("Segoe UI", 11, "bold")).pack(pady=(0,2))

        tk.Label(bank_frame,
                 text="• HDFC Bank   • ICICI Bank   • SBI • Axis Bank   • American Express",
                 bg="#F9D895", fg="#001DF6", font=("Segoe UI", 10)).pack()

        # --- Upload Frame ---
        upload_frame = tk.Frame(root, bg="#F9D895", pady=18)
        upload_frame.pack()

        self.file_label = tk.Label(upload_frame, text="No file selected",
                                   bg="#F9D895", fg="#001DF6", font=("Segoe UI", 10, "italic"))
        self.file_label.grid(row=0, column=0, padx=15)

        self.upload_btn = ttk.Button(upload_frame, text="📂 Select PDF", command=self.load_pdf)
        self.upload_btn.grid(row=0, column=1, padx=10)

        self.parse_btn = ttk.Button(upload_frame, text="🔍 Parse PDF", command=self.parse_pdf)
        self.parse_btn.grid(row=0, column=2, padx=10)

        # --- Results Frame ---
        result_frame = tk.LabelFrame(root, text=" Extracted Data ",
                                     bg="#FBE4B7", fg="#27374D", font=("Segoe UI", 12, "bold"),
                                     labelanchor="n", padx=20, pady=20)
        result_frame.pack(fill="both", expand=True, padx=20, pady=(6, 12))

        self.tree = ttk.Treeview(result_frame, columns=("Field", "Value"), show="headings", height=9)
        self.tree.heading("Field", text="Data Field")
        self.tree.heading("Value", text="Extracted Value")
        self.tree.column("Field", width=220, anchor="center")
        self.tree.column("Value", width=400, anchor="center")
        self.tree.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", background="#27374D", foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10), background="#FBE4B7", fieldbackground="#FBE4B7", rowheight=30)
        style.map("Treeview", background=[("selected", "#5789A8")])

        # --- Footer ---
        footer = tk.Label(root, text="Developed by Shabbir Hardwarewala",
                          bg="#27374D", fg="white", pady=8, font=("Segoe UI", 10))
        footer.pack(side="bottom", fill="x")

        self.pdf_path = None

    def load_pdf(self):
        file_path = filedialog.askopenfilename(title="Select Credit Card Statement PDF",
                                               filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_path = file_path
            filename = file_path.split("/")[-1]
            # make file name clearly visible: bold and navy color
            self.file_label.config(text=f"📄 {filename}", fg="#27374D", font=("Segoe UI", 10, "bold"))

    def parse_pdf(self):
        if not self.pdf_path:
            messagebox.showwarning("No File Selected", "Please select a PDF file first.")
            return

        try:
            data = extract_data_from_pdf(self.pdf_path)
            self.display_data(data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse PDF.\n\nError: {e}")

    def display_data(self, data):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for key, value in data.items():
            self.tree.insert("", "end", values=(key, value))

# ---------------------- Run App ----------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = CreditCardParserApp(root)
    root.mainloop()
