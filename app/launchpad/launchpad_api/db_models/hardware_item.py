from datetime import datetime
from sqlalchemy.exc import IntegrityError
import logging
from ..db import db
import traceback

class HardwareItem(db.Model):
    __tablename__ = 'hardware_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('hardware_categories.id'), nullable=False)
    subcategory = db.Column(db.String(255), nullable=True)
    manufacturer = db.Column(db.String(255), nullable=True)
    configuration_notes = db.Column(db.Text, nullable=True)
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False)
    support_type = db.Column(db.String(255), nullable=True)
    support_cost = db.Column(db.Numeric(10, 2), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(255), nullable=True)
    updated_by = db.Column(db.String(255), nullable=True)

    def __init__(self, name, category_id, unit_cost, description=None, subcategory=None,
                 manufacturer=None, configuration_notes=None, support_type=None,
                 support_cost=None, is_active=True, created_by=None, updated_by=None):
        self.name = name
        self.category_id = category_id
        self.unit_cost = unit_cost
        self.description = description
        self.subcategory = subcategory
        self.manufacturer = manufacturer
        self.configuration_notes = configuration_notes
        self.support_type = support_type
        self.support_cost = support_cost
        self.is_active = is_active
        self.created_by = created_by
        self.updated_by = updated_by

    def __repr__(self):
        return f"<HardwareItem(id={self.id}, name='{self.name}', category_id={self.category_id})>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "category_id": str(self.category_id),
            "subcategory": self.subcategory,
            "manufacturer": self.manufacturer,
            "configuration_notes": self.configuration_notes,
            "unit_cost": float(self.unit_cost) if self.unit_cost else None,
            "support_type": self.support_type,
            "support_cost": float(self.support_cost) if self.support_cost else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "category": self.category.to_dict() if self.category else None
        }

    def create_row(self):
        """Insert a new HardwareItem record into the database."""
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
        """Commit changes made to this HardwareItem record."""
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    def delete_row(self):
        """Delete this HardwareItem record from the database."""
        try:
            # Use query-based delete to avoid session state issues
            # This works regardless of whether the object is attached or detached
            deleted_count = HardwareItem.query.filter_by(id=self.id).delete()
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
            logging.error(f"[HardwareItem.delete_row] IntegrityError: {str(e)}")
            logging.error(f"[HardwareItem.delete_row] Full traceback: {exceptionstring}")
            print(exceptionstring)
            # Re-raise IntegrityError so controller can handle it properly
            raise
        except Exception as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            error_type = type(e).__name__
            logging.error(f"[HardwareItem.delete_row] Error ({error_type}): {str(e)}")
            logging.error(f"[HardwareItem.delete_row] Full traceback: {exceptionstring}")
            print(exceptionstring)
            # Re-raise other exceptions so controller can handle them
            raise

    @staticmethod
    def get_by_id(item_id):
        """Fetch a HardwareItem record safely by ID."""
        try:
            item = HardwareItem.query.get(item_id)
            return item
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None

    @staticmethod
    def get_all(category_ids=None, active_only=False):
        """Fetch all HardwareItem records with optional filters."""
        try:
            query = HardwareItem.query
            if category_ids:
                query = query.filter(HardwareItem.category_id.in_(category_ids))
            if active_only:
                query = query.filter(HardwareItem.is_active == True)
            return query.all()
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None

