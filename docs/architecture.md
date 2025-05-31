# Architecture

## Technologies
- Frontend: HTML/CSS/JavaScript
- Backend: Flask (Python)
- Database: SQLite
- ML: scikit-learn + joblib

## Modules
- `app.py` – Main Flask app
- `models/transaction_model.py` – Database model
- `train_expense_model.py` – ML pipeline
- `app.js` – Frontend logic

## Diagram
User → Frontend (form + list) → API (/transactions, /predict) → DB + ML model