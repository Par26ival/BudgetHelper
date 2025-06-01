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
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            if not User.query.filter_by(username="testuser").first():
                user = User(username="testuser")
                user.set_password("12345")
                db.session.add(user)
                db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def login(client):
    return client.post("/login", json={
        "username": "testuser",
        "password": "12345"
    }, follow_redirects=True)

def test_add_transaction(client):
    login_response = login(client)
    assert login_response.status_code == 200

    response = client.post("/transactions", json={
        "amount": 100.0,
        "description": "Test payment",
        "type": "income",
        "date": "2025-06-01"
    })
    assert response.status_code == 201

def test_get_transactions(client):
    login_response = login(client)
    assert login_response.status_code == 200

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
    login_response = login(client)
    assert login_response.status_code == 200

    add_tx_resp = client.post("/transactions", json={
        "amount": 200.0,
        "description": "Salary",
        "type": "income",
        "date": "2025-06-01"
    })
    assert add_tx_resp.status_code == 201

    response = client.get("/predict")
    assert response.status_code == 200
    data = response.get_json()

    assert "total_spending" in data
    assert "total_income" in data
    assert "net_savings" in data
