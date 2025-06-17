import pandas as pd
from extensions import db
from app import app
from models.transaction_model import Transaction

df = pd.read_csv("transactions.csv")

with app.app_context():
    db.drop_all()
    db.create_all()

    for _, row in df.iterrows():
        tx = Transaction(
            description=row["description"],
            amount=row["amount"],
            category=row["category"],
            type=row["category"] if row["category"] == "income" else "spending",
            date=row["date"],
        )
        db.session.add(tx)

    db.session.commit()

print("✅ Loaded transactions from CSV into the database.")
