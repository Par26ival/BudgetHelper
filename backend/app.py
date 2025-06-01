from flask import Flask, request, jsonify, redirect, url_for, send_from_directory, abort
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

app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path=""
)

CORS(app)
Swagger(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///transactions.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()

model = joblib.load(os.path.join(os.path.dirname(__file__), "model.joblib"))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect('/index.html')
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return jsonify({"message": "Already logged in", "redirect": "/index.html"}), 200

    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return jsonify({"message": "Login successful", "redirect": "/index.html"}), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 401

    return send_from_directory(app.static_folder, 'login.html')

@app.route('/index.html')
@login_required
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return jsonify({"message": "Account created successfully", "redirect": "/index.html"}), 201

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route("/transactions", methods=["GET"])
@login_required
def get_transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    return jsonify([t.to_dict() for t in transactions])

@app.route("/transactions/<int:user_id>", methods=["GET"])
@login_required
def get_transactions_by_user(user_id):
    if current_user.id != user_id:
        abort(403, description="Access forbidden")
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    return jsonify([t.to_dict() for t in transactions])

@app.route("/transactions", methods=["POST"])
@login_required
def add_transaction():
    data = request.get_json()
    description = data.get("description")
    amount = data.get("amount")
    date = data.get("date")
    type_ = data.get("type", "spending")

    if type_ == "income":
        category = "income"
    else:
        dt = pd.to_datetime(date)
        input_df = pd.DataFrame([{
            "amount": amount,
            "description": description,
            "day": dt.day,
            "weekday": dt.weekday(),
            "month": dt.month,
        }])
        category = model.predict(input_df)[0]

    new_transaction = Transaction(
        description=description,
        amount=amount,
        category=category,
        type=type_,
        date=date,
        user_id=current_user.id
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify(new_transaction.to_dict()), 201

@app.route("/predict", methods=["GET"])
@login_required
def predict():
    cutoff_date = datetime.utcnow().date() - timedelta(days=30)

    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= cutoff_date
    ).all()

    if not transactions:
        return jsonify({
            "message": "No transactions found in the last 30 days",
            "total_spending": 0.0,
            "total_income": 0.0,
            "net_savings": 0.0,
        })

    total_spending = 0.0
    total_income = 0.0

    for t in transactions:
        if (t.category and t.category.lower() == "income") or t.type == "income":
            total_income += t.amount
        else:
            total_spending += t.amount

    net_savings = total_income - total_spending

    return jsonify({
        "total_spending": round(total_spending, 2),
        "total_income": round(total_income, 2),
        "net_savings": round(net_savings, 2),
        "transaction_count": len(transactions),
        "message": "Summary of your transactions in the last 30 days",
    })

@app.route("/api/stats/monthly")
@login_required
def monthly_stats():
    cutoff_date = datetime.utcnow().date() - timedelta(days=90)

    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= cutoff_date
    ).all()

    if not transactions:
        return jsonify([])

    df = pd.DataFrame([t.to_dict() for t in transactions])
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month")["amount"].sum().reset_index()
    monthly = monthly.rename(columns={"amount": "total_spent"})
    return jsonify(monthly.to_dict(orient="records"))

@app.route('/check_transactions')
@login_required
def check_transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    if not transactions:
        return "No transactions found for current user."
    return "<br>".join([f"{tx.date} - {tx.description} - {tx.amount} - {tx.type}" for tx in transactions])

if __name__ == "__main__":
    app.run(debug=True)
