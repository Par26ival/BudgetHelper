import csv
from extensions import db
from app import app
from models.transaction_model import Transaction

# Read CSV file
transactions = []
with open("transactions.csv", "r") as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        transactions.append(row)

with app.app_context():
    db.drop_all()
    db.create_all()

    for row in transactions:
        tx = Transaction(
            description=row["description"],
            amount=float(row["amount"]),
            category=row["category"],
            type=row["category"] if row["category"] == "income" else "spending",
            date=row["date"],
        )
        db.session.add(tx)

    db.session.commit()

print("✅ Loaded transactions from CSV into the database.")
