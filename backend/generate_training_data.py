import pandas as pd
from datetime import datetime, timedelta
import random

start_date = datetime(2025, 2, 1)
end_date = datetime(2025, 5, 1)

data = []

def add_repeating(description, category, amount, start, interval_days, occurrences, jitter=0):
    for i in range(occurrences):
        date = start + timedelta(days=interval_days * i + random.randint(-jitter, jitter))
        if date < end_date:
            data.append({
                "description": description,
                "category": category,
                "amount": round(amount * random.uniform(0.95, 1.05), 2),
                "date": date.date().isoformat()
            })

# 🏠 Monthly bills
add_repeating("Monthly rent", "housing", 500, datetime(2025, 2, 1), 30, 3)
add_repeating("Home insurance", "housing", 60, datetime(2025, 2, 3), 30, 3)

# 💵 Income
add_repeating("Monthly salary", "income", 1500, datetime(2025, 2, 1), 30, 3)
add_repeating("Freelance job", "income", 450, datetime(2025, 2, 15), 30, 3)

# 🛒 Food (2-3x/week)
food_days = pd.date_range(start=start_date, end=end_date, freq="3D")
for d in food_days:
    data.append({
        "description": random.choice(["Groceries Lidl", "Lunch Subway", "McDonald's breakfast"]),
        "category": "food",
        "amount": round(random.uniform(7, 35), 2),
        "date": d.date().isoformat()
    })

# 🚇 Transport
add_repeating("Monthly metro pass", "transport", 15, datetime(2025, 2, 1), 30, 3)
add_repeating("Uber ride", "transport", 10, datetime(2025, 2, 5), 7, 12)

# 📺 Subscriptions
add_repeating("Netflix", "entertainment", 19.99, datetime(2025, 2, 1), 30, 3)
add_repeating("Spotify", "entertainment", 9.99, datetime(2025, 2, 2), 30, 3)

# 💊 Health
add_repeating("Pharmacy supplies", "health", 12, datetime(2025, 2, 10), 28, 3)
add_repeating("Clinic visit", "health", 35, datetime(2025, 2, 20), 30, 3)

# 🧴 Personal
add_repeating("Haircut", "personal", 18, datetime(2025, 2, 6), 30, 3)
add_repeating("Period supplies", "personal", 14, datetime(2025, 2, 4), 28, 3)

# 🛍 Shopping (random)
shopping_days = pd.date_range(start=start_date, end=end_date, freq="10D")
for d in shopping_days:
    data.append({
        "description": random.choice(["New shoes", "T-shirt Zara", "DM cosmetics"]),
        "category": "shopping",
        "amount": round(random.uniform(20, 80), 2),
        "date": d.date().isoformat()
    })

# 📶 Utilities
add_repeating("Electric bill", "utilities", 90, datetime(2025, 2, 5), 30, 3)
add_repeating("Internet", "utilities", 40, datetime(2025, 2, 7), 30, 3)

# Final dataset
df = pd.DataFrame(data)
df.to_csv("transactions.csv", index=False)
print(f"✅ Generated {len(df)} rows of realistic training data in transactions.csv")
