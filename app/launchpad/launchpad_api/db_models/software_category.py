from datetime import datetime
from ..db import db
import traceback

class SoftwareCategory(db.Model):
    __tablename__ = 'software_categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to SoftwareModule
    modules = db.relationship('SoftwareModule', backref=db.backref('category', lazy=True))

    def __init__(self, name, description=None, is_active=True):
        self.name = name
        self.description = description
        self.is_active = is_active

    def __repr__(self):
        return f"<SoftwareCategory(id={self.id}, name='{self.name}')>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def create_row(self):
        """Insert a new SoftwareCategory record into the database."""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    def update_row(self):
        """Commit changes made to this SoftwareCategory record."""
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    def delete_row(self):
        """Delete this SoftwareCategory record from the database."""
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
    def get_by_id(category_id):
        """Fetch a SoftwareCategory record safely by ID."""
        try:
            category = SoftwareCategory.query.get(category_id)
            return category
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None

    @staticmethod
    def get_all(active_only=False):
        """Fetch all SoftwareCategory records."""
        try:
            query = SoftwareCategory.query
            if active_only:
                query = query.filter(SoftwareCategory.is_active == True)
            return query.all()
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None

