from datetime import datetime
from sqlalchemy.exc import IntegrityError
import logging
from ..db import db
import traceback

class RecommendationRule(db.Model):
    __tablename__ = 'recommendation_rules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    software_category_id = db.Column(db.Integer, db.ForeignKey('software_categories.id'), nullable=False)
    hardware_category_id = db.Column(db.Integer, db.ForeignKey('hardware_categories.id'), nullable=False)
    is_mandatory = db.Column(db.Boolean, default=False, nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    software_category = db.relationship('SoftwareCategory', foreign_keys=[software_category_id])
    hardware_category = db.relationship('HardwareCategory', foreign_keys=[hardware_category_id])

    def __init__(self, software_category_id, hardware_category_id, is_mandatory=False, quantity=1):
        self.software_category_id = software_category_id
        self.hardware_category_id = hardware_category_id
        self.is_mandatory = is_mandatory
        self.quantity = quantity

    def __repr__(self):
        return f"<RecommendationRule(id={self.id}, software_category_id={self.software_category_id}, hardware_category_id={self.hardware_category_id})>"

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "software_category": str(self.software_category_id),
            "hardware_category": str(self.hardware_category_id),
            "is_mandatory": self.is_mandatory,
            "quantity": self.quantity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def create_row(self):
        """Insert a new RecommendationRule record into the database."""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None  # Return None for duplicate/constraint violations
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    def update_row(self):
        """Commit changes made to this RecommendationRule record."""
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    def delete_row(self):
        """Delete this RecommendationRule record from the database."""
        try:
            # Ensure object is in session by merging (handles both attached and detached objects)
            obj_to_delete = db.session.merge(self)
            db.session.delete(obj_to_delete)
            db.session.commit()
            return self.id
        except IntegrityError as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[RecommendationRule.delete_row] IntegrityError: {str(e)}")
            logging.error(f"[RecommendationRule.delete_row] Full traceback: {exceptionstring}")
            print(exceptionstring)
            # Re-raise IntegrityError so controller can handle it properly
            raise
        except Exception as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            error_type = type(e).__name__
            logging.error(f"[RecommendationRule.delete_row] Error ({error_type}): {str(e)}")
            logging.error(f"[RecommendationRule.delete_row] Full traceback: {exceptionstring}")
            print(exceptionstring)
            # Re-raise other exceptions so controller can handle them
            raise

    @staticmethod
    def get_by_id(rule_id):
        """Fetch a RecommendationRule record safely by ID."""
        try:
            rule = RecommendationRule.query.get(rule_id)
            return rule
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None

    @staticmethod
    def get_all(category_ids=None):
        """Fetch all RecommendationRule records with optional filters.
        
        Args:
            category_ids: List of software category IDs to filter by.
                         Only filters by software_category_id, not hardware_category_id.
        """
        try:
            query = RecommendationRule.query
            if category_ids:
                # Filter only by software_category_id (not hardware_category_id)
                query = query.filter(RecommendationRule.software_category_id.in_(category_ids))
            
            # Order by software_category_id, then is_mandatory (DESC), then hardware_category_id
            query = query.order_by(
                RecommendationRule.software_category_id,
                RecommendationRule.is_mandatory.desc(),
                RecommendationRule.hardware_category_id
            )
            
            return query.all()
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None

    @staticmethod
    def get_by_categories(software_category_id, hardware_category_id, exclude_id=None):
        """Check if a recommendation rule exists for the given category combination.
        
        Args:
            software_category_id: Software category ID
            hardware_category_id: Hardware category ID
            exclude_id: Optional rule ID to exclude from check (for updates)
        
        Returns:
            RecommendationRule if found, None otherwise
        """
        try:
            query = RecommendationRule.query.filter_by(
                software_category_id=software_category_id,
                hardware_category_id=hardware_category_id
            )
            if exclude_id:
                query = query.filter(RecommendationRule.id != exclude_id)
            return query.first()
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None

