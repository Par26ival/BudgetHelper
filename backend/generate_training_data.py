import pandas as pd
from datetime import datetime, timedelta
import random

data = []

def add_repeating(description, category, amount, start, end, interval_days, jitter=0, fluctuation=0.15):
    date = start
    while date <= end:
        varied_amount = round(amount * random.uniform(1 - fluctuation, 1 + fluctuation), 2)
        data.append({
            "description": description,
            "category": category,
            "amount": varied_amount,
            "date": date.date().isoformat()
        })
        date += timedelta(days=interval_days + random.randint(-jitter, jitter))

# Phase 1: Original range
add_repeating("Monthly rent", "housing", 500, datetime(2025, 1, 1), datetime(2025, 4, 30), 30)
add_repeating("Monthly salary", "income", 1500, datetime(2025, 1, 1), datetime(2025, 4, 30), 30)
add_repeating("Netflix subscription", "entertainment", 19.99, datetime(2025, 1, 2), datetime(2025, 4, 30), 30)
add_repeating("Internet service", "utilities", 40, datetime(2025, 1, 5), datetime(2025, 4, 30), 30)
add_repeating("Electric bill", "utilities", 90, datetime(2025, 1, 6), datetime(2025, 4, 30), 30)
add_repeating("Groceries", "food", 60, datetime(2025, 1, 3), datetime(2025, 4, 30), 14, jitter=3)
add_repeating("Lunch Subway", "food", 12, datetime(2025, 1, 4), datetime(2025, 4, 30), 7, jitter=2)
add_repeating("Uber ride", "transport", 10, datetime(2025, 1, 5), datetime(2025, 4, 30), 5, jitter=1)
add_repeating("Pharmacy supplies", "health", 15, datetime(2025, 1, 8), datetime(2025, 4, 30), 21, jitter=2)
add_repeating("Period supplies", "personal", 14, datetime(2025, 1, 10), datetime(2025, 4, 30), 28)
add_repeating("Haircut", "personal", 18, datetime(2025, 1, 12), datetime(2025, 4, 30), 30)

# Random shopping (original)
random_days1 = pd.date_range(start="2025-01-01", end="2025-05-01", freq="8D")
for d in random_days1:
    data.append({
        "description": random.choice(["New jacket", "Shoes", "Zara T-shirt", "Tech gadget", "Home decor"]),
        "category": "shopping",
        "amount": round(random.uniform(25, 100), 2),
        "date": d.date().isoformat()
    })

# 🔥 Phase 2: May to August 2025 (extension)
add_repeating("Monthly rent", "housing", 500, datetime(2025, 5, 1), datetime(2025, 8, 31), 30)
add_repeating("Monthly salary", "income", 1500, datetime(2025, 5, 1), datetime(2025, 8, 31), 30)
add_repeating("Netflix subscription", "entertainment", 19.99, datetime(2025, 5, 2), datetime(2025, 8, 31), 30)
add_repeating("Internet service", "utilities", 40, datetime(2025, 5, 5), datetime(2025, 8, 31), 30)
add_repeating("Electric bill", "utilities", 90, datetime(2025, 5, 6), datetime(2025, 8, 31), 30)
add_repeating("Groceries", "food", 60, datetime(2025, 5, 3), datetime(2025, 8, 31), 14, jitter=3)
add_repeating("Lunch Subway", "food", 12, datetime(2025, 5, 4), datetime(2025, 8, 31), 7, jitter=2)
add_repeating("Uber ride", "transport", 10, datetime(2025, 5, 5), datetime(2025, 8, 31), 5, jitter=1)
add_repeating("Pharmacy supplies", "health", 15, datetime(2025, 5, 8), datetime(2025, 8, 31), 21, jitter=2)
add_repeating("Period supplies", "personal", 14, datetime(2025, 5, 10), datetime(2025, 8, 31), 28)
add_repeating("Haircut", "personal", 18, datetime(2025, 5, 12), datetime(2025, 8, 31), 30)

# Random shopping (extension)
random_days2 = pd.date_range(start="2025-05-02", end="2025-08-31", freq="8D")
for d in random_days2:
    data.append({
        "description": random.choice(["Sneakers", "Bluetooth speaker", "Summer dress", "AC service", "Books"]),
        "category": "shopping",
        "amount": round(random.uniform(30, 110), 2),
        "date": d.date().isoformat()
    })

# Export all to CSV
df = pd.DataFrame(data)
df.to_csv("transactions.csv", index=False)
print(f"✅ Extended dataset to {len(df)} total transactions up to end of August 2025.")
