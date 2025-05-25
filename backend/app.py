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
        input_df = pd.DataFrame([{
            "amount": amount,
            "description": description,
            "day": dt.day,
            "weekday": dt.weekday(),
            "month": dt.month
        }])
        category = model.predict(input_df)[0]

    new_transaction = Transaction(
        description=description,
        amount=amount,
        category=category,
        type=type_,
        date=date
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify(new_transaction.to_dict()), 201



@app.route("/predict", methods=["GET"])
def predict_next():
    transactions = Transaction.query.all()
    df = pd.DataFrame([t.to_dict() for t in transactions])
    predictions = []
    total_income = 0
    total_spending = 0

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        grouped = df.groupby(["description", "type"])

        for (desc, typ), group in grouped:
            if len(group) < 2:
                continue

            group = group.sort_values("date")
            deltas = group["date"].diff().dropna().dt.days
            avg_days = int(deltas.mean())

            last_date = group["date"].max()
            predicted_date = last_date + timedelta(days=avg_days)

            if predicted_date.month != last_date.month:
                # Only show next-month predictions
                predictions.append({
                    "description": desc,
                    "type": typ,
                    "date": predicted_date.date().isoformat(),
                    "amount": group["amount"].mean()
                })

                if typ == "income":
                    total_income += group["amount"].mean()
                else:
                    total_spending += group["amount"].mean()

    return jsonify({
        "predictions": predictions,
        "total_income": round(total_income, 2),
        "total_spending": round(total_spending, 2),
        "net_savings": round(total_income - total_spending, 2)
    })


if __name__ == "__main__":
    app.run(debug=True)
