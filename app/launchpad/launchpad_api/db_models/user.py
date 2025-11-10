from datetime import datetime
from launchpad_api.db import db
import traceback

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    last_logged_in = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name, email, last_logged_in=None):
        self.name = name
        self.email = email
        if last_logged_in:
            self.last_logged_in = last_logged_in

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"

    # --- CRUD OPERATIONS ---

    def create_row(self):
        """Insert a new User record into the database."""
        try:
            db.session.add(self)
            db.session.commit()
            return self.id
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    def update_row(self):
        """Commit changes made to this User record."""
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    def delete_row(self):
        """Delete this User record from the database."""
        try:
            db.session.delete(self)
            db.session.commit()
            return self.id
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    @staticmethod
    def get_by_id( user_id):
        """Fetch a User record safely by ID."""
        try:
            user = User.query.get(user_id)
            return user
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None

    @staticmethod
    def get_by_email( email):
        """Fetch a User by email."""
        try:
            user = User.query.filter_by(User.email==email).first()
            return user
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None

    @staticmethod
    def get_all_users():
        try:
            users = User.query.all()
            return users
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None