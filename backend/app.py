from flask import Flask, request, jsonify, redirect, url_for, send_from_directory
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
    static_folder="../frontend",    # JS, CSS, and HTML (all in one folder)
    static_url_path=""              # serve static files from root url
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
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

model = joblib.load(os.path.join(os.path.dirname(__file__), "model.joblib"))

# Redirect root '/' to '/login' or '/index.html' based on authentication
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect('/index.html')
    else:
        return redirect(url_for('login'))

# Login route serves login page on GET, handles login on POST
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

    # GET request: serve login.html page from static folder
    return send_from_directory(app.static_folder, 'login.html')

# Serve index.html as static file (protected route)
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
    # Redirect to login page (served as static)
    return redirect('/')

@app.route("/transactions", methods=["GET"])
@login_required
def get_transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
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
def predict_next_30_days():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    if not transactions:
        return jsonify({
            "forecast": [],
            "total_income": 0.0,
            "total_spending": 0.0,
            "net_savings": 0.0,
        })

    df = pd.DataFrame([t.to_dict() for t in transactions])
    df["date"] = pd.to_datetime(df["date"])
    today = datetime.today()
    end_date = today + timedelta(days=30)

    def normalize(desc):
        desc = desc.lower()
        keywords = {
            "rent": "rent",
            "salary": "salary",
            "pad": "period supplies",
            "period": "period supplies",
            "spotify": "spotify",
            "netflix": "netflix",
            "lidl": "groceries",
            "billa": "groceries",
            "grocer": "groceries",
            "electric": "electric bill",
            "internet": "internet",
        }
        for k, v in keywords.items():
            if k in desc:
                return v
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
        occurrences = max(1, (30 // avg_days))
        total_amount = round(avg_amount * occurrences, 2)

        predicted_date = last_date + timedelta(days=avg_days)
        if predicted_date.date() <= end_date.date():
            forecast.append({
                "description": desc,
                "type": typ,
                "date": predicted_date.date().isoformat(),
                "amount": avg_amount,
                "expected_occurrences": occurrences,
                "total_estimate": total_amount,
            })
            if typ == "income":
                total_income += total_amount
            else:
                total_spending += total_amount

    return jsonify({
        "forecast": forecast,
        "total_income": round(total_income, 2),
        "total_spending": round(total_spending, 2),
        "net_savings": round(total_income - total_spending, 2),
    })

@app.route("/api/stats/monthly")
@login_required
def monthly_stats():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    if not transactions:
        return jsonify([])

    df = pd.DataFrame([t.to_dict() for t in transactions])
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month")["amount"].sum().reset_index()
    monthly = monthly.rename(columns={"amount": "total_spent"})
    return jsonify(monthly.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
