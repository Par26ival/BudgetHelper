import pandas as pd
from datetime import datetime, timedelta
import random

from app import app
from extensions import db
from models.transaction_model import Transaction
from models.user_model import User

# 👉 Set your target username
USERNAME = "Kaloyan"

data = []


# Helper to assign type
def get_type(category):
    return "income" if category == "income" else "spending"


# Repeating transaction generator with date validation
def add_repeating(
    description, category, amount, start, end, interval_days, jitter=0, fluctuation=0.15
):
    date = start
    used_dates = set()  # Track used dates to prevent duplicates

    while date <= end:
        # Add jitter to the date
        jittered_date = date + timedelta(days=random.randint(-jitter, jitter))

        # Skip if date is already used or outside our range
        if jittered_date.date().isoformat() in used_dates or jittered_date > end:
            date += timedelta(days=interval_days)
            continue

        used_dates.add(jittered_date.date().isoformat())
        varied_amount = round(
            amount * random.uniform(1 - fluctuation, 1 + fluctuation), 2
        )

        data.append(
            {
                "description": description,
                "category": category,
                "amount": varied_amount,
                "type": get_type(category),
                "date": jittered_date.date().isoformat(),
            }
        )
        date += timedelta(days=interval_days)


# 🔁 Phase 1: Jan–Apr 2024 (using current year)
current_year = datetime.now().year
add_repeating(
    "Monthly rent",
    "housing",
    500,
    datetime(current_year, 1, 1),
    datetime(current_year, 4, 30),
    30,
)
add_repeating(
    "Monthly salary",
    "income",
    1500,
    datetime(current_year, 1, 1),
    datetime(current_year, 4, 30),
    30,
)
add_repeating(
    "Netflix subscription",
    "entertainment",
    19.99,
    datetime(current_year, 1, 2),
    datetime(current_year, 4, 30),
    30,
)
add_repeating(
    "Internet service",
    "utilities",
    40,
    datetime(current_year, 1, 5),
    datetime(current_year, 4, 30),
    30,
)
add_repeating(
    "Electric bill",
    "utilities",
    90,
    datetime(current_year, 1, 6),
    datetime(current_year, 4, 30),
    30,
)
add_repeating(
    "Groceries",
    "food",
    60,
    datetime(current_year, 1, 3),
    datetime(current_year, 4, 30),
    14,
    jitter=3,
)
add_repeating(
    "Lunch Subway",
    "food",
    12,
    datetime(current_year, 1, 4),
    datetime(current_year, 4, 30),
    7,
    jitter=2,
)
add_repeating(
    "Uber ride",
    "transport",
    10,
    datetime(current_year, 1, 5),
    datetime(current_year, 4, 30),
    5,
    jitter=1,
)
add_repeating(
    "Pharmacy supplies",
    "health",
    15,
    datetime(current_year, 1, 8),
    datetime(current_year, 4, 30),
    21,
    jitter=2,
)
add_repeating(
    "Haircut",
    "personal",
    18,
    datetime(current_year, 1, 12),
    datetime(current_year, 4, 30),
    30,
)

# 🛍️ Random shopping with date validation
used_dates = set()
random_days1 = pd.date_range(
    start=f"{current_year}-01-01", end=f"{current_year}-04-30", freq="8D"
)
for d in random_days1:
    date_str = d.date().isoformat()
    if date_str not in used_dates:
        used_dates.add(date_str)
        data.append(
            {
                "description": random.choice(
                    ["New jacket", "Shoes", "Zara T-shirt", "Tech gadget", "Home decor"]
                ),
                "category": "shopping",
                "amount": round(random.uniform(25, 100), 2),
                "type": "spending",
                "date": date_str,
            }
        )

# 🔁 Phase 2: May–Aug 2024
add_repeating(
    "Monthly rent",
    "housing",
    500,
    datetime(current_year, 5, 1),
    datetime(current_year, 8, 31),
    30,
)
add_repeating(
    "Monthly salary",
    "income",
    1500,
    datetime(current_year, 5, 1),
    datetime(current_year, 8, 31),
    30,
)
add_repeating(
    "Netflix subscription",
    "entertainment",
    19.99,
    datetime(current_year, 5, 2),
    datetime(current_year, 8, 31),
    30,
)
add_repeating(
    "Internet service",
    "utilities",
    40,
    datetime(current_year, 5, 5),
    datetime(current_year, 8, 31),
    30,
)
add_repeating(
    "Electric bill",
    "utilities",
    90,
    datetime(current_year, 5, 6),
    datetime(current_year, 8, 31),
    30,
)
add_repeating(
    "Groceries",
    "food",
    60,
    datetime(current_year, 5, 3),
    datetime(current_year, 8, 31),
    14,
    jitter=3,
)
add_repeating(
    "Lunch Subway",
    "food",
    12,
    datetime(current_year, 5, 4),
    datetime(current_year, 8, 31),
    7,
    jitter=2,
)
add_repeating(
    "Uber ride",
    "transport",
    10,
    datetime(current_year, 5, 5),
    datetime(current_year, 8, 31),
    5,
    jitter=1,
)
add_repeating(
    "Pharmacy supplies",
    "health",
    15,
    datetime(current_year, 5, 8),
    datetime(current_year, 8, 31),
    21,
    jitter=2,
)
add_repeating(
    "Haircut",
    "personal",
    18,
    datetime(current_year, 5, 12),
    datetime(current_year, 8, 31),
    30,
)

# 🛍️ Random shopping (May–Aug) with date validation
random_days2 = pd.date_range(
    start=f"{current_year}-05-02", end=f"{current_year}-08-31", freq="8D"
)
for d in random_days2:
    date_str = d.date().isoformat()
    if date_str not in used_dates:
        used_dates.add(date_str)
        data.append(
            {
                "description": random.choice(
                    [
                        "Sneakers",
                        "Bluetooth speaker",
                        "Summer dress",
                        "AC service",
                        "Books",
                    ]
                ),
                "category": "shopping",
                "amount": round(random.uniform(30, 110), 2),
                "type": "spending",
                "date": date_str,
            }
        )

# Sort data by date
data.sort(key=lambda x: x["date"])

# 🚀 Insert into database
with app.app_context():
    user = User.query.filter_by(username=USERNAME).first()
    if not user:
        print(f"❌ No user found with username '{USERNAME}'.")
    else:
        # Clear existing transactions for this user
        Transaction.query.filter_by(user_id=user.id).delete()
        db.session.commit()

        count = 0
        for entry in data:
            tx = Transaction(
                user_id=user.id,
                description=entry["description"],
                category=entry["category"],
                amount=entry["amount"],
                type=entry["type"],
                date=entry["date"],
            )
            db.session.add(tx)
            count += 1
        db.session.commit()
        print(f"✅ {count} transactions inserted for user '{USERNAME}' (ID {user.id}).")
