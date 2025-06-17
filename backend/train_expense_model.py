import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from datetime import datetime

# 1. Simulated dataset
data = [
    {
        "amount": 5.20,
        "description": "Coffee at Starbucks",
        "category": "food",
        "date": "2025-05-02",
    },
    {
        "amount": 12.00,
        "description": "Lunch at Subway",
        "category": "food",
        "date": "2025-05-03",
    },
    {
        "amount": 7.50,
        "description": "Breakfast at McDonald's",
        "category": "food",
        "date": "2025-05-04",
    },
    {
        "amount": 20.00,
        "description": "Dinner at Pizza Hut",
        "category": "food",
        "date": "2025-05-10",
    },
    {
        "amount": 35.00,
        "description": "Groceries from Lidl",
        "category": "food",
        "date": "2025-05-05",
    },
    {
        "amount": 50.00,
        "description": "Groceries from Billa",
        "category": "food",
        "date": "2025-05-19",
    },
    {
        "amount": 100.00,
        "description": "Monthly grocery shopping",
        "category": "food",
        "date": "2025-05-01",
    },
    {
        "amount": 2.60,
        "description": "Bus ticket",
        "category": "transport",
        "date": "2025-05-07",
    },
    {
        "amount": 15.00,
        "description": "Monthly metro fee",
        "category": "transport",
        "date": "2025-05-01",
    },
    {
        "amount": 18.00,
        "description": "Train to Plovdiv",
        "category": "transport",
        "date": "2025-05-18",
    },
    {
        "amount": 22.00,
        "description": "Taxi ride downtown",
        "category": "transport",
        "date": "2025-05-15",
    },
    {
        "amount": 35.00,
        "description": "Fuel at OMV",
        "category": "transport",
        "date": "2025-05-12",
    },
    {
        "amount": 12.00,
        "description": "Uber ride to mall",
        "category": "transport",
        "date": "2025-05-09",
    },
    {
        "amount": 9.99,
        "description": "Spotify monthly subscription",
        "category": "entertainment",
        "date": "2025-05-01",
    },
    {
        "amount": 19.99,
        "description": "Netflix subscription",
        "category": "entertainment",
        "date": "2025-05-01",
    },
    {
        "amount": 70.00,
        "description": "Manicure and pedicure",
        "category": "personal",
        "date": "2025-05-16",
    },
    {
        "amount": 8.00,
        "description": "Barbershop",
        "category": "personal",
        "date": "2025-05-27",
    },
]

# Convert data to numpy arrays
amounts = np.array([item["amount"] for item in data])
descriptions = np.array([item["description"] for item in data])
categories = np.array([item["category"] for item in data])
dates = np.array([datetime.fromisoformat(item["date"]) for item in data])

# Extract temporal features
days = np.array([dt.day for dt in dates])
weekdays = np.array([dt.weekday() for dt in dates])
months = np.array([dt.month for dt in dates])

# Combine features
X = np.column_stack([amounts, days, weekdays, months])
y = categories

# 5. Define column transformer (numeric features only now)
preprocessor = StandardScaler()

# 6. Build pipeline: preprocess + classifier
pipeline = make_pipeline(
    preprocessor, RandomForestClassifier(n_estimators=100, random_state=42)
)

# 7. Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 8. Fit model
pipeline.fit(X_train, y_train)

# 9. Save trained model
joblib.dump(pipeline, "model.joblib")
print("✅ Model trained with temporal features. Saved as model.joblib.")
