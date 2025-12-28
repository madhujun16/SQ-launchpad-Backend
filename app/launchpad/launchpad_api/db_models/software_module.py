from datetime import datetime
from sqlalchemy.exc import IntegrityError
import logging
from ..db import db
import traceback

class SoftwareModule(db.Model):
    __tablename__ = 'software_modules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('software_categories.id'), nullable=False)
    license_fee = db.Column(db.Numeric(10, 2), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to SoftwareCategory is defined via backref in SoftwareCategory model

    def __init__(self, name, category_id, description=None, license_fee=None, is_active=True):
        self.name = name
        self.category_id = category_id
        self.description = description
        self.license_fee = license_fee
        self.is_active = is_active

    def __repr__(self):
        return f"<SoftwareModule(id={self.id}, name='{self.name}', category_id={self.category_id})>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "category_id": str(self.category_id),
            "license_fee": float(self.license_fee) if self.license_fee else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "category": self.category.to_dict() if self.category else None
        }

    def create_row(self):
        """Insert a new SoftwareModule record into the database."""
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
        """Commit changes made to this SoftwareModule record."""
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    def delete_row(self):
        """Delete this SoftwareModule record from the database."""
        try:
            # Use query-based delete to avoid session state issues
            # This works regardless of whether the object is attached or detached
            deleted_count = SoftwareModule.query.filter_by(id=self.id).delete()
            if deleted_count > 0:
                db.session.commit()
                return self.id
            else:
                # Object doesn't exist or already deleted
                db.session.rollback()
                return None
        except IntegrityError as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[SoftwareModule.delete_row] IntegrityError: {str(e)}")
            logging.error(f"[SoftwareModule.delete_row] Full traceback: {exceptionstring}")
            print(exceptionstring)
            # Re-raise IntegrityError so controller can handle it properly
            raise
        except Exception as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            error_type = type(e).__name__
            logging.error(f"[SoftwareModule.delete_row] Error ({error_type}): {str(e)}")
            logging.error(f"[SoftwareModule.delete_row] Full traceback: {exceptionstring}")
            print(exceptionstring)
            # Re-raise other exceptions so controller can handle them
            raise

    @staticmethod
    def get_by_id(module_id):
        """Fetch a SoftwareModule record safely by ID."""
        try:
            module = SoftwareModule.query.get(module_id)
            return module
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None

    @staticmethod
    def get_all(category_ids=None, active_only=False):
        """Fetch all SoftwareModule records with optional filters."""
        try:
            query = SoftwareModule.query
            if category_ids:
                query = query.filter(SoftwareModule.category_id.in_(category_ids))
            if active_only:
                query = query.filter(SoftwareModule.is_active == True)
            return query.all()
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None

