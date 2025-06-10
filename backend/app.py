from flask import (
    Flask,
    request,
    jsonify,
    redirect,
    url_for,
    send_from_directory,
    abort,
    session,
)
from flask_cors import CORS
from models.transaction_model import Transaction
from models.user_model import User
from extensions import db, login_manager
from flask_login import login_user, logout_user, login_required, current_user
from flasgger import Swagger
import joblib
import os
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__, static_folder="../frontend", static_url_path="")

# Configure CORS properly
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5000", "http://127.0.0.1:5000"],
    allow_headers=["Content-Type"],
    methods=["GET", "POST", "OPTIONS"],
)

# Configure session
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
app.config["SECRET_KEY"] = "your_secret_key_here"

Swagger(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///transactions.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()

model = joblib.load(os.path.join(os.path.dirname(__file__), "model.joblib"))


@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect("/index.html")
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/index.html")

    if request.method == "POST":
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            session.permanent = True
            return (
                jsonify(
                    {
                        "message": "Login successful",
                        "redirect": "/index.html",
                        "user": {"id": user.id, "username": user.username},
                    }
                ),
                200,
            )
        else:
            return jsonify({"message": "Invalid username or password"}), 401

    return send_from_directory(app.static_folder, "login.html")


@app.route("/index.html")
@login_required
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user, remember=True)
    session.permanent = True
    return (
        jsonify(
            {
                "message": "Account created successfully",
                "redirect": "/index.html",
                "user": {"id": new_user.id, "username": new_user.username},
            }
        ),
        201,
    )


@app.route("/logout")
@login_required
def logout():
    session.clear()
    logout_user()
    return jsonify({"message": "Logged out successfully", "redirect": "/login"}), 200


@app.route("/transactions", methods=["GET"])
@login_required
def get_transactions():
    try:
        transactions = (
            Transaction.query.filter_by(user_id=current_user.id)
            .order_by(Transaction.date.desc())
            .all()
        )
        return jsonify([t.to_dict() for t in transactions])
    except Exception as e:
        print(f"Error fetching transactions: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/transactions", methods=["POST"])
@login_required
def add_transaction():
    try:
        data = request.get_json()
        description = data.get("description")
        amount = data.get("amount")
        date = data.get("date")
        type_ = data.get("type", "spending")

        if type_ == "income":
            category = "income"
        else:
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
            description=description,
            amount=amount,
            category=category,
            type=type_,
            date=date,
            user_id=current_user.id,
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify(new_transaction.to_dict()), 201
    except Exception as e:
        print(f"Error adding transaction: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/predict", methods=["GET"])
@login_required
def predict():
    try:
        today = datetime.utcnow().date()
        print(f"[PREDICT] Backend 'today' date: {today}")
        cutoff_date = today - timedelta(days=30)
        print(f"Fetching transactions from {cutoff_date} to {today}")

        # Get transactions from the last 30 days
        transactions = (
            Transaction.query.filter(
                Transaction.user_id == current_user.id,
                Transaction.date >= cutoff_date,
                Transaction.date <= today,
            )
            .order_by(Transaction.date.desc())
            .all()
        )

        # Calculate average daily spending
        spending = [t.amount for t in transactions if t.type != "income"]
        total_spending = sum(spending)
        days_with_spending = len(
            set(t.date for t in transactions if t.type != "income")
        )
        avg_daily_spending = (
            total_spending / days_with_spending if days_with_spending else 0
        )
        predicted_spending = avg_daily_spending * 30

        # Predict income: use the most recent income transaction (simulate monthly salary)
        income_transactions = [t for t in transactions if t.type == "income"]
        if income_transactions:
            # Use the most recent income as the prediction
            predicted_income = income_transactions[0].amount
        else:
            predicted_income = 0.0

        # Category breakdown for spending
        spending_by_category = {}
        for t in transactions:
            if t.type != "income":
                category = t.category if t.category else "uncategorized"
                spending_by_category[category] = (
                    spending_by_category.get(category, 0) + t.amount
                )

        result = {
            "predicted_spending": round(predicted_spending, 2),
            "predicted_income": round(predicted_income, 2),
            "spending_by_category": {
                k: round(v, 2) for k, v in spending_by_category.items()
            },
            "message": "Prediction for the next 30 days",
            "period": "Next 30 days",
        }
        return jsonify(result)
    except Exception as e:
        print(f"Error generating prediction: {str(e)}")
        import traceback

        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
