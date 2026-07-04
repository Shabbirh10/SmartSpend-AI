from app.services.parser import parser
transactions = parser.extract_transactions('/Users/shabbirhardwarewala/Desktop/Projects/smartspend/demo_statement.pdf')
print("Total transactions:", len(transactions))
for t in transactions[:5]:
    print(t)
