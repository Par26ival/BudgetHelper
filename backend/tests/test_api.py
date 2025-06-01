import json
import sys
import os
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, db
from models import User

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            user = User(username="testuser")
            user.set_password("testpass")
            db.session.add(user)
            db.session.commit()

        # Log in the test user
        client.post("/login", data={
            "username": "testuser1",
            "password": "testpass1"
        })

        yield client

        # Cleanup
        with app.app_context():
            db.session.remove()
            db.drop_all()

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