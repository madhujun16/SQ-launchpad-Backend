from datetime import datetime
from db import db
import traceback

class Site(db.Model):
    __tablename__ = 'site'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name, status='active'):
        self.name = name
        self.status = status

    def __repr__(self):
        return f"<Site(id={self.id}, name='{self.name}', status='{self.status}')>"

    # --- CRUD OPERATIONS ---

    def create_row(self):
        """Insert a new Site record into the database."""
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
        """Commit changes made to an existing Site record."""
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    def delete_row(self):
        """Delete this Site record from the database."""
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
    def get_by_id(site_id):
        """Fetch a Site record safely by ID."""
        try:
            site = Site.query.get(site_id)
            return site
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None
