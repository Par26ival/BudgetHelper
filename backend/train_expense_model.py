import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

# 1. Simulated dataset
data = [
    {"amount": 5.20, "description": "Coffee at Starbucks", "category": "food", "date": "2025-05-02"},
    {"amount": 12.00, "description": "Lunch at Subway", "category": "food", "date": "2025-05-03"},
    {"amount": 7.50, "description": "Breakfast at McDonald's", "category": "food", "date": "2025-05-04"},
    {"amount": 20.00, "description": "Dinner at Pizza Hut", "category": "food", "date": "2025-05-10"},
    {"amount": 35.00, "description": "Groceries from Lidl", "category": "food", "date": "2025-05-05"},
    {"amount": 50.00, "description": "Groceries from Billa", "category": "food", "date": "2025-05-19"},
    {"amount": 100.00, "description": "Monthly grocery shopping", "category": "food", "date": "2025-05-01"},
    {"amount": 2.60, "description": "Bus ticket", "category": "transport", "date": "2025-05-07"},
    {"amount": 15.00, "description": "Monthly metro fee", "category": "transport", "date": "2025-05-01"},
    {"amount": 18.00, "description": "Train to Plovdiv", "category": "transport", "date": "2025-05-18"},
    {"amount": 22.00, "description": "Taxi ride downtown", "category": "transport", "date": "2025-05-15"},
    {"amount": 35.00, "description": "Fuel at OMV", "category": "transport", "date": "2025-05-12"},
    {"amount": 12.00, "description": "Uber ride to mall", "category": "transport", "date": "2025-05-09"},
    {"amount": 9.99, "description": "Spotify monthly subscription", "category": "entertainment", "date": "2025-05-01"},
    {"amount": 19.99, "description": "Netflix subscription", "category": "entertainment", "date": "2025-05-01"},
    {"amount": 8.00, "description": "Movie ticket", "category": "entertainment", "date": "2025-05-11"},
    {"amount": 25.00, "description": "Bowling night", "category": "entertainment", "date": "2025-05-17"},
    {"amount": 30.00, "description": "Theatre play", "category": "entertainment", "date": "2025-05-23"},
    {"amount": 65.00, "description": "Concert ticket", "category": "entertainment", "date": "2025-05-26"},
    {"amount": 70.00, "description": "New running shoes", "category": "shopping", "date": "2025-05-06"},
    {"amount": 120.00, "description": "Jacket from Zara", "category": "shopping", "date": "2025-05-08"},
    {"amount": 35.00, "description": "T-shirt and jeans", "category": "shopping", "date": "2025-05-10"},
    {"amount": 25.00, "description": "Cosmetics from DM", "category": "shopping", "date": "2025-05-15"},
    {"amount": 200.00, "description": "Smartwatch from Technopolis", "category": "shopping", "date": "2025-05-20"},
    {"amount": 49.00, "description": "Bluetooth speaker", "category": "shopping", "date": "2025-05-21"},
    {"amount": 85.00, "description": "Electric bill", "category": "utilities", "date": "2025-05-04"},
    {"amount": 60.00, "description": "Water bill", "category": "utilities", "date": "2025-05-08"},
    {"amount": 45.00, "description": "Internet service", "category": "utilities", "date": "2025-05-10"},
    {"amount": 30.00, "description": "Mobile phone plan", "category": "utilities", "date": "2025-05-11"},
    {"amount": 110.00, "description": "Heating for the month", "category": "utilities", "date": "2025-05-05"},
    {"amount": 35.00, "description": "Clinic check-up", "category": "health", "date": "2025-05-13"},
    {"amount": 15.00, "description": "Pharmacy meds", "category": "health", "date": "2025-05-14"},
    {"amount": 70.00, "description": "Dental cleaning", "category": "health", "date": "2025-05-16"},
    {"amount": 55.00, "description": "Optician visit", "category": "health", "date": "2025-05-21"},
    {"amount": 25.00, "description": "Therapy session", "category": "health", "date": "2025-05-28"},
    {"amount": 400.00, "description": "Monthly rent", "category": "housing", "date": "2025-05-01"},
    {"amount": 850.00, "description": "Apartment rental payment", "category": "housing", "date": "2025-05-01"},
    {"amount": 200.00, "description": "Property tax", "category": "housing", "date": "2025-05-02"},
    {"amount": 60.00, "description": "Maintenance fee", "category": "housing", "date": "2025-05-03"},
    {"amount": 250.00, "description": "Home insurance", "category": "housing", "date": "2025-05-04"},
    {"amount": 1500.00, "description": "Monthly salary", "category": "income", "date": "2025-05-01"},
    {"amount": 400.00, "description": "Freelance payment", "category": "income", "date": "2025-05-15"},
    {"amount": 800.00, "description": "Project bonus", "category": "income", "date": "2025-05-22"},
    {"amount": 200.00, "description": "Sold old laptop", "category": "income", "date": "2025-05-19"},
    {"amount": 100.00, "description": "Refund from Amazon", "category": "income", "date": "2025-05-14"},
    {"amount": 25.00, "description": "Online course fee", "category": "education", "date": "2025-05-06"},
    {"amount": 12.00, "description": "Textbook purchase", "category": "education", "date": "2025-05-07"},
    {"amount": 150.00, "description": "Tuition payment", "category": "education", "date": "2025-05-10"},
    {"amount": 9.99, "description": "Coursera subscription", "category": "education", "date": "2025-05-01"},
    {"amount": 35.00, "description": "Language course", "category": "education", "date": "2025-05-11"},
    {"amount": 18.00, "description": "Haircut", "category": "personal", "date": "2025-05-12"},
    {"amount": 40.00, "description": "Gym membership", "category": "personal", "date": "2025-05-01"},
    {"amount": 25.00, "description": "Massage session", "category": "personal", "date": "2025-05-20"},
    {"amount": 70.00, "description": "Manicure and pedicure", "category": "personal", "date": "2025-05-16"},
    {"amount": 8.00, "description": "Barbershop", "category": "personal", "date": "2025-05-27"}
]


#df = pd.DataFrame(data)
df = pd.read_csv("transactions.csv")

# 2. Convert 'date' column to datetime
df["date"] = pd.to_datetime(df["date"])

# 3. Extract temporal features
df["day"] = df["date"].dt.day
df["weekday"] = df["date"].dt.weekday  # 0 = Monday
df["month"] = df["date"].dt.month

# 4. Select features and target
X = df[["amount", "description", "day", "weekday", "month"]]
y = df["category"]

# 5. Define column transformer (numeric + text + time features)
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), ["amount", "day", "weekday", "month"]),
        ("text", TfidfVectorizer(), "description")
    ]
)

# 6. Build pipeline: preprocess + classifier
pipeline = make_pipeline(preprocessor, RandomForestClassifier(n_estimators=100, random_state=42))

# 7. Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 8. Fit model
pipeline.fit(X_train, y_train)

# 9. Save trained model
joblib.dump(pipeline, "model.joblib")
print("✅ Model trained with temporal and textual features. Saved as model.joblib.")