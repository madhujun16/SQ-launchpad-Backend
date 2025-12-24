from datetime import datetime
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
            db.session.delete(self)
            db.session.commit()
            return self.id
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

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
        """Fetch all RecommendationRule records with optional filters."""
        try:
            query = RecommendationRule.query
            if category_ids:
                query = query.filter(
                    (RecommendationRule.software_category_id.in_(category_ids)) |
                    (RecommendationRule.hardware_category_id.in_(category_ids))
                )
            return query.all()
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None

