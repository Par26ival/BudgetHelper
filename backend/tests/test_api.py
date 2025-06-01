import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, db
from models.user_model import User

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["LOGIN_DISABLED"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create test user if not exists
            if not User.query.filter_by(username="testuse1").first():
                user = User(username="testuser1")
                user.set_password("testpass1")
                db.session.add(user)
                db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def login(client):
    return client.post("/login", data={
        "username": "testuser1",
        "password": "testpass1"
    }, follow_redirects=True)

def test_add_transaction(client):
    login(client)
    response = client.post("/transactions", json={
        "amount": 100.0,
        "description": "Test payment",
        "type": "income",
        "date": "2025-06-01"
    })
    assert response.status_code == 201

def test_get_transactions(client):
    login(client)
    client.post("/transactions", json={
        "amount": 50.0,
        "description": "Groceries",
        "type": "expense",
        "date": "2025-06-01"
    })
    response = client.get("/transactions")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(tx["description"] == "Groceries" for tx in data)

def test_prediction_endpoint(client):
    login(client)
    response = client.get("/predict")
    assert response.status_code == 200
    data = response.get_json()
    assert "total_spent" in data
    assert "total_income" in data
    assert "predicted_savings" in data
