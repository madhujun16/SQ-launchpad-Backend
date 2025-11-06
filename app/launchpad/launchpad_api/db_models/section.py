from datetime import datetime
from db import db
import traceback

class Section(db.Model):
    __tablename__ = 'section'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section_name = db.Column(db.String(255), nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to Page model
    page = db.relationship('Page', backref=db.backref('sections', lazy=True))

    def __init__(self, section_name, page_id):
        self.section_name = section_name
        self.page_id = page_id

    def __repr__(self):
        return f"<Section(id={self.id}, section_name='{self.section_name}', page_id={self.page_id})>"

    # --- CRUD Operations ---

    def create_row(self):
        """Insert a new Section record into the database."""
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
        """Commit updates made to this Section record."""
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    def delete_row(self):
        """Delete this Section record from the database."""
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
    def get_by_id(section_id):
        """Fetch a Section record safely by ID."""
        try:
            section = Section.query.get(section_id)
            return section
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None
