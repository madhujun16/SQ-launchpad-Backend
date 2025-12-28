from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete
import logging
from ..db import db
import traceback
import json

class ApprovalAction(db.Model):
    __tablename__ = 'approval_actions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    approval_id = db.Column(db.Integer, db.ForeignKey('scoping_approvals.id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 'submit', 'approve', 'reject', 'request_changes', 'resubmit'
    performed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    performed_by_role = db.Column(db.String(50), nullable=False)
    performed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comment = db.Column(db.Text, nullable=True)
    metadata = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    approval = db.relationship('ScopingApproval', backref=db.backref('actions', lazy=True))
    performer = db.relationship('User', backref='approval_actions')

    def __init__(self, approval_id, action, performed_by, performed_by_role, comment=None, metadata=None):
        self.approval_id = approval_id
        self.action = action
        self.performed_by = performed_by
        self.performed_by_role = performed_by_role
        self.comment = comment
        self.metadata = metadata if isinstance(metadata, dict) else json.loads(metadata) if isinstance(metadata, str) else metadata

    def __repr__(self):
        return f"<ApprovalAction(id={self.id}, approval_id={self.approval_id}, action='{self.action}')>"

    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            'id': str(self.id),
            'approval_id': str(self.approval_id),
            'action': self.action,
            'performed_by': str(self.performed_by),
            'performed_by_role': self.performed_by_role,
            'performed_at': self.performed_at.isoformat() if self.performed_at else None,
            'comment': self.comment,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def create_row(self, commit=True):
        """Insert a new ApprovalAction record into the database."""
        try:
            db.session.add(self)
            db.session.flush()
            if commit:
                db.session.commit()
            return self.id
        except IntegrityError as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[ApprovalAction.create_row] IntegrityError: {str(e)}")
            logging.error(f"[ApprovalAction.create_row] Full traceback: {exceptionstring}")
            raise
        except Exception as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[ApprovalAction.create_row] Error: {str(e)}")
            logging.error(f"[ApprovalAction.create_row] Full traceback: {exceptionstring}")
            raise

    @staticmethod
    def get_by_approval_id(approval_id):
        """Get all actions for a specific approval."""
        try:
            actions = ApprovalAction.query.filter_by(approval_id=approval_id).order_by(ApprovalAction.performed_at.desc()).all()
            return actions
        except Exception:
            exceptionstring = traceback.format_exc()
            logging.error(f"[ApprovalAction.get_by_approval_id] Error: {exceptionstring}")
            return None

