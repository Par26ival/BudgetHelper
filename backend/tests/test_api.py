import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


def test_add_transaction():
    with app.test_client() as client:
        response = client.post("/transactions", json={
            "amount": 100.0,
            "description": "Test payment",
            "type": "income",
            "date": "2025-06-01"
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data["description"] == "Test payment"

def test_get_transactions():
    with app.test_client() as client:
        response = client.get("/transactions")
        assert response.status_code == 200
        assert isinstance(response.get_json(), list)

def test_prediction_endpoint():
    with app.test_client() as client:
        response = client.get("/predict")
        assert response.status_code == 200
        data = response.get_json()
        assert "forecast" in data
        assert "total_income" in data