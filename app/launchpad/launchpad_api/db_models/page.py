from datetime import datetime
from db import db
import traceback

class Page(db.Model):
    __tablename__ = 'page'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    page_name = db.Column(db.String(255), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to Site model
    site = db.relationship('Site', backref=db.backref('pages', lazy=True))

    def __init__(self, page_name, site_id):
        self.page_name = page_name
        self.site_id = site_id

    def __repr__(self):
        return f"<Page(id={self.id}, page_name='{self.page_name}', site_id={self.site_id})>"

    # --- CRUD Operations ---
    def create_row(self):
        """Insert a new Page record into the database."""
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
        """Commit updates made to this Page record."""
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    def delete_row(self):
        """Delete this Page record from the database."""
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
    def get_by_id(page_id):
        """Fetch a Page record safely by ID."""
        try:
            page = Page.query.get(page_id)
            return page
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None
