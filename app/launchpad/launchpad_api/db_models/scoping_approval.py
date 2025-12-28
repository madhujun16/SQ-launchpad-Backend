from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete
import logging
from ..db import db
import traceback
import json

class ScopingApproval(db.Model):
    __tablename__ = 'scoping_approvals'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id', ondelete='CASCADE'), nullable=False)
    site_name = db.Column(db.String(255), nullable=False)
    deployment_engineer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    deployment_engineer_name = db.Column(db.String(255), nullable=False)
    ops_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ops_manager_name = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='pending')  # 'pending', 'approved', 'rejected', 'changes_requested'
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    review_comment = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    scoping_data = db.Column(db.JSON, nullable=False)  # Contains selected_software and selected_hardware
    cost_breakdown = db.Column(db.JSON, nullable=False)  # Contains cost summary
    version = db.Column(db.Integer, nullable=False, default=1)
    previous_version_id = db.Column(db.Integer, db.ForeignKey('scoping_approvals.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    site = db.relationship('Site', backref=db.backref('scoping_approvals', lazy=True))
    deployment_engineer = db.relationship('User', foreign_keys=[deployment_engineer_id], backref='submitted_approvals')
    ops_manager = db.relationship('User', foreign_keys=[ops_manager_id], backref='managed_approvals')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_approvals')
    previous_version = db.relationship('ScopingApproval', remote_side=[id], backref='next_versions')

    def __init__(self, site_id, site_name, deployment_engineer_id, deployment_engineer_name,
                 scoping_data, cost_breakdown, ops_manager_id=None, ops_manager_name=None,
                 status='pending', version=1, previous_version_id=None):
        self.site_id = site_id
        self.site_name = site_name
        self.deployment_engineer_id = deployment_engineer_id
        self.deployment_engineer_name = deployment_engineer_name
        self.ops_manager_id = ops_manager_id
        self.ops_manager_name = ops_manager_name
        self.status = status
        self.scoping_data = scoping_data if isinstance(scoping_data, dict) else json.loads(scoping_data) if isinstance(scoping_data, str) else scoping_data
        self.cost_breakdown = cost_breakdown if isinstance(cost_breakdown, dict) else json.loads(cost_breakdown) if isinstance(cost_breakdown, str) else cost_breakdown
        self.version = version
        self.previous_version_id = previous_version_id

    def __repr__(self):
        return f"<ScopingApproval(id={self.id}, site_id={self.site_id}, status='{self.status}')>"

    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            'id': str(self.id),
            'site_id': str(self.site_id),
            'site_name': self.site_name,
            'deployment_engineer_id': str(self.deployment_engineer_id),
            'deployment_engineer_name': self.deployment_engineer_name,
            'ops_manager_id': str(self.ops_manager_id) if self.ops_manager_id else None,
            'ops_manager_name': self.ops_manager_name,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'reviewed_by': str(self.reviewed_by) if self.reviewed_by else None,
            'review_comment': self.review_comment,
            'rejection_reason': self.rejection_reason,
            'scoping_data': self.scoping_data,
            'cost_breakdown': self.cost_breakdown,
            'version': self.version,
            'previous_version_id': str(self.previous_version_id) if self.previous_version_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def create_row(self, commit=True):
        """Insert a new ScopingApproval record into the database."""
        try:
            db.session.add(self)
            db.session.flush()
            if commit:
                db.session.commit()
            return self.id
        except IntegrityError as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[ScopingApproval.create_row] IntegrityError: {str(e)}")
            logging.error(f"[ScopingApproval.create_row] Full traceback: {exceptionstring}")
            raise
        except Exception as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[ScopingApproval.create_row] Error: {str(e)}")
            logging.error(f"[ScopingApproval.create_row] Full traceback: {exceptionstring}")
            raise

    def update_row(self, commit=True):
        """Commit changes made to an existing ScopingApproval record."""
        try:
            self.updated_at = datetime.utcnow()
            db.session.add(self)
            if commit:
                db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[ScopingApproval.update_row] IntegrityError: {str(e)}")
            logging.error(f"[ScopingApproval.update_row] Full traceback: {exceptionstring}")
            raise
        except Exception as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[ScopingApproval.update_row] Error: {str(e)}")
            logging.error(f"[ScopingApproval.update_row] Full traceback: {exceptionstring}")
            raise

    def delete_row(self):
        """Delete this ScopingApproval record from the database."""
        try:
            # Use SQLAlchemy delete statement for maximum reliability
            stmt = delete(ScopingApproval).where(ScopingApproval.id == self.id)
            result = db.session.execute(stmt)
            deleted_count = result.rowcount
            
            if deleted_count > 0:
                db.session.commit()
                return self.id
            else:
                db.session.rollback()
                return None
        except IntegrityError as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[ScopingApproval.delete_row] IntegrityError: {str(e)}")
            logging.error(f"[ScopingApproval.delete_row] Full traceback: {exceptionstring}")
            raise
        except Exception as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            error_type = type(e).__name__
            logging.error(f"[ScopingApproval.delete_row] Error ({error_type}): {str(e)}")
            logging.error(f"[ScopingApproval.delete_row] Full traceback: {exceptionstring}")
            raise

    @staticmethod
    def get_by_id(approval_id):
        """Fetch a ScopingApproval record safely by ID."""
        try:
            approval = ScopingApproval.query.get(approval_id)
            return approval
        except Exception:
            exceptionstring = traceback.format_exc()
            logging.error(f"[ScopingApproval.get_by_id] Error: {exceptionstring}")
            return None

    @staticmethod
    def get_by_site_id(site_id, status=None):
        """Get the most recent scoping approval for a site, optionally filtered by status."""
        try:
            query = ScopingApproval.query.filter_by(site_id=site_id)
            if status:
                query = query.filter_by(status=status)
            # Get the most recent one (highest version or latest created_at)
            approval = query.order_by(ScopingApproval.version.desc(), ScopingApproval.created_at.desc()).first()
            return approval
        except Exception:
            exceptionstring = traceback.format_exc()
            logging.error(f"[ScopingApproval.get_by_site_id] Error: {exceptionstring}")
            return None

    @staticmethod
    def get_pending_by_site_id(site_id):
        """Check if there's a pending approval for a site."""
        try:
            approval = ScopingApproval.query.filter_by(site_id=site_id, status='pending').first()
            return approval
        except Exception:
            exceptionstring = traceback.format_exc()
            logging.error(f"[ScopingApproval.get_pending_by_site_id] Error: {exceptionstring}")
            return None

    @staticmethod
    def get_all(status=None, site_id=None):
        """Fetch all ScopingApproval records with optional filters."""
        try:
            query = ScopingApproval.query
            if status:
                query = query.filter_by(status=status)
            if site_id:
                query = query.filter_by(site_id=site_id)
            # Order by most recent first
            approvals = query.order_by(ScopingApproval.created_at.desc()).all()
            return approvals
        except Exception:
            exceptionstring = traceback.format_exc()
            logging.error(f"[ScopingApproval.get_all] Error: {exceptionstring}")
            return None

