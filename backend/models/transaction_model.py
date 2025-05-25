from extensions import db
from datetime import datetime


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False, default="spending")
    date = db.Column(
        db.String(10), nullable=False, default=datetime.utcnow().date().isoformat()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "category": self.category,
            "type": self.type,
            "date": self.date,
        }
