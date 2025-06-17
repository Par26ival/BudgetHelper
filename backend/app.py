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
import numpy as np
from datetime import datetime, timedelta, timezone
from collections import Counter
import json

app = Flask(__name__, static_folder="../frontend/build", static_url_path="")

# Configure CORS properly
CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "https://tomovi.eu",
        "https://*.vercel.app",
    ],
    allow_headers=["Content-Type"],
    methods=["GET", "POST", "OPTIONS"],
)

# Configure session
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=10)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your_secret_key_here")

# Configure database for Vercel
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///transactions.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

Swagger(app)

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

# Load model
model = joblib.load(os.path.join(os.path.dirname(__file__), "model.joblib"))

# Create tables if they don't exist
with app.app_context():
    db.create_all()


@login_manager.unauthorized_handler
def unauthorized():
    return redirect("/login")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def home():
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
        response = jsonify([t.to_dict() for t in transactions])
        # Add user info to response headers
        response.headers["X-User-Info"] = json.dumps(
            {"username": current_user.username, "id": current_user.id}
        )
        return response
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
        today = datetime.now(timezone.utc)
        print(f"[PREDICT] Backend 'today' date: {today}")
        cutoff_date = today - timedelta(days=30)  # Look at last 30 days
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

        # Calculate total income from last 30 days
        income_transactions = [t for t in transactions if t.type == "income"]
        total_income = sum(t.amount for t in income_transactions)

        # Calculate total spending and spending by category from last 30 days
        spending_transactions = [t for t in transactions if t.type != "income"]
        total_spending = sum(t.amount for t in spending_transactions)

        # Group spending by category
        spending_by_category = {}
        for t in spending_transactions:
            category = t.category if t.category else "uncategorized"
            spending_by_category[category] = (
                spending_by_category.get(category, 0) + t.amount
            )

        result = {
            "predicted_spending": round(total_spending, 2),
            "predicted_income": round(total_income, 2),
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
    app.run()
