from datetime import datetime
from launchpad_api.db import db
import traceback

class Site(db.Model):
    __tablename__ = 'site'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(50), nullable=False, default='created')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, status='created'):
        self.status = status

    def __repr__(self):
        return f"<Site(id={self.id}, status='{self.status}')>"

    # --- CRUD OPERATIONS ---

    def create_row(self,commit=True):
        """Insert a new Site record into the database."""
        try:
            db.session.add(self)
            if commit and not db.session.in_transaction():
                db.session.commit()
            return self.id
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    def update_row(self,commit=True):
        """Commit changes made to an existing Site record."""
        try:
            db.session.add(self)
            if commit:
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
    
    @staticmethod
    def delete_by_id(site_id):
        """Delete a Site record safely by its ID."""
        try:
            site = Site.query.get(site_id)
            if not site:
                return False  # Site not found
            db.session.delete(site)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            import traceback
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    @staticmethod
    def get_all_sites():
        try:
            all_sites = Site.query.all()
            return all_sites
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None
    
   