from extensions import db

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False, default='spending') # 'income' or 'spending'
    date = db.Column(db.String(100), nullable=False) # Store date as string

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Foreign key to User

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "category": self.category,
            "type": self.type,
            "date": self.date,
            "user_id": self.user_id
        }