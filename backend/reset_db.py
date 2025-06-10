import os
from app import app, db
from models.user_model import User
from models.transaction_model import Transaction


def reset_database():
    # Delete existing database files
    db_files = ["transactions.db", "users.db"]
    for file in db_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Deleted {file}")

    # Create new database
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Created new database tables")

        # Create test users
        test_users = [("testuser", "testpass"), ("user2", "pass2")]

        for username, password in test_users:
            if not User.query.filter_by(username=username).first():
                user = User(username=username)
                user.set_password(password)
                db.session.add(user)
                print(f"Created user: {username}")

        db.session.commit()
        print("Database reset complete!")


if __name__ == "__main__":
    reset_database()
