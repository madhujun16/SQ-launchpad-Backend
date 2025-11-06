from datetime import datetime
from db import db
import traceback

class Field(db.Model):
    __tablename__ = 'field'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    field_name = db.Column(db.String(255), nullable=False)
    field_value = db.Column(db.JSON, nullable=True)  # stores JSON data
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to Section model
    section = db.relationship('Section', backref=db.backref('fields', lazy=True))

    def __init__(self, field_name, field_value, section_id):
        self.field_name = field_name
        self.field_value = field_value
        self.section_id = section_id

    def __repr__(self):
        return f"<Field(id={self.id}, field_name='{self.field_name}', section_id={self.section_id})>"

    # --- CRUD operations ---
    def create_row(self):
        """Create a new Field record."""
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
        """Commit any updates made to this Field."""
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    def delete_row(self):
        """Delete this Field record."""
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
    def get_by_id(field_id):
        """Fetch a Field record safely by ID."""
        try:
            field = Field.query.get(field_id)
            return field
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None
