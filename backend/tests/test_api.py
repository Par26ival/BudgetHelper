import json
import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, db
from models.user_model import User

@pytest.fixture(scope="function")
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()

        # Only create user if not already present (in memory DB is fresh each test)
        if not User.query.filter_by(username="testuser1").first():
            user = User(username="testuser1")
            user.set_password("testpass1")
            db.session.add(user)
            db.session.commit()

    with app.test_client() as client:
        # Login
        client.post("/login", data={
            "username": "testuser1",
            "password": "testpass1"
        })
        yield client

    # No need to drop db, memory DB is gone after function scope

def test_add_transaction(client):
    response = client.post("/transactions", json={
        "amount": 100.0,
        "description": "Test payment",
        "type": "income",
        "date": "2025-06-01"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["description"] == "Test payment"

def test_get_transactions(client):
    client.post("/transactions", json={
        "amount": 50.0,
        "description": "Groceries",
        "type": "expense",
        "date": "2025-06-01"
    })
    response = client.get("/transactions")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_prediction_endpoint(client):
    response = client.get("/predict")
    assert response.status_code == 200
    data = response.get_json()
    assert "forecast" in data
    assert "total_income" in data
