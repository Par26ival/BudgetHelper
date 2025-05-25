from flask import Flask, request, jsonify
from flask_cors import CORS
from models.transaction_model import Transaction
from extensions import db
import joblib
import os
import pandas as pd
from datetime import datetime, timedelta


app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///transactions.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

model = joblib.load(os.path.join(os.path.dirname(__file__), "model.joblib"))


@app.route("/transactions", methods=["GET"])
def get_transactions():
    transactions = Transaction.query.all()
    return jsonify([t.to_dict() for t in transactions])


@app.route("/transactions", methods=["POST"])
def add_transaction():
    data = request.get_json()
    description = data.get("description")
    amount = data.get("amount")
    date = data.get("date")
    type_ = data.get("type", "spending")

    if type_ == "income":
        category = "income"
    else:
        # Extract day, weekday, month
        dt = pd.to_datetime(date)
        input_df = pd.DataFrame(
            [
                {
                    "amount": amount,
                    "description": description,
                    "day": dt.day,
                    "weekday": dt.weekday(),
                    "month": dt.month,
                }
            ]
        )
        category = model.predict(input_df)[0]

    new_transaction = Transaction(
        description=description, amount=amount, category=category, type=type_, date=date
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify(new_transaction.to_dict()), 201


@app.route("/predict", methods=["GET"])
def predict_next_30_days():
    transactions = Transaction.query.all()
    if not transactions:
        return jsonify({
            "forecast": [],
            "total_income": 0.0,
            "total_spending": 0.0,
            "net_savings": 0.0
        })

    df = pd.DataFrame([t.to_dict() for t in transactions])
    df["date"] = pd.to_datetime(df["date"])

    today = datetime.today()
    end_date = today + timedelta(days=30)

    # Normalize descriptions
    def normalize(desc):
        desc = desc.lower()
        if "rent" in desc: return "rent"
        if "salary" in desc: return "salary"
        if "pad" in desc or "period" in desc: return "period supplies"
        if "spotify" in desc: return "spotify"
        if "netflix" in desc: return "netflix"
        if "grocer" in desc or "lidl" in desc or "billa" in desc: return "groceries"
        if "electric" in desc: return "electric bill"
        if "internet" in desc: return "internet"
        return desc

    df["normalized"] = df["description"].apply(normalize)

    forecast = []
    total_income = 0.0
    total_spending = 0.0

    grouped = df.groupby(["normalized", "type"])

    for (desc, typ), group in grouped:
        if len(group) < 2:
            continue

        group = group.sort_values("date")
        deltas = group["date"].diff().dropna().dt.days
        if deltas.empty:
            continue

        avg_days = int(deltas.mean())
        if avg_days > 90 or avg_days == 0:
            continue

        avg_amount = round(group["amount"].mean(), 2)
        last_date = group["date"].max()

        # How many times will this transaction occur in the next 30 days?
        occurrences = max(1, (30 // avg_days))  # Ensure at least 1 if avg_days < 30
        total_amount = round(avg_amount * occurrences, 2)

        # Forecast next occurrence
        predicted_date = last_date + timedelta(days=avg_days)
        if predicted_date.date() <= end_date.date():
            forecast.append({
                "description": desc,
                "type": typ,
                "date": predicted_date.date().isoformat(),
                "amount": avg_amount,
                "expected_occurrences": occurrences,
                "total_estimate": total_amount
            })

            if typ == "income":
                total_income += total_amount
            else:
                total_spending += total_amount

    return jsonify({
        "forecast": forecast,
        "total_income": round(total_income, 2),
        "total_spending": round(total_spending, 2),
        "net_savings": round(total_income - total_spending, 2)
    })


if __name__ == "__main__":
    app.run(debug=True)
