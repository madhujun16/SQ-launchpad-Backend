from datetime import datetime, date
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete
import logging
from ..db import db
import traceback

class ProcurementData(db.Model):
    __tablename__ = 'procurement_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id', ondelete='CASCADE'), nullable=False)
    delivery_date = db.Column(db.Date, nullable=True)
    delivery_receipt_url = db.Column(db.String(500), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='draft')  # 'draft', 'completed'
    completed_at = db.Column(db.DateTime, nullable=True)
    completed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    site = db.relationship('Site', backref=db.backref('procurement_data', lazy=True))
    completed_by_user = db.relationship('User', foreign_keys=[completed_by], backref='completed_procurements')

    def __init__(self, site_id, delivery_date=None, delivery_receipt_url=None, summary=None, 
                 status='draft', completed_by=None):
        self.site_id = site_id
        self.delivery_date = delivery_date
        self.delivery_receipt_url = delivery_receipt_url
        self.summary = summary
        self.status = status
        self.completed_by = completed_by
        if status == 'completed' and not self.completed_at:
            self.completed_at = datetime.utcnow()

    def __repr__(self):
        return f"<ProcurementData(id={self.id}, site_id={self.site_id}, status='{self.status}')>"

    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            'id': str(self.id),
            'site_id': str(self.site_id),
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'delivery_receipt_url': self.delivery_receipt_url,
            'summary': self.summary,
            'status': self.status,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'completed_by': str(self.completed_by) if self.completed_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def create_row(self, commit=True):
        """Insert a new ProcurementData record into the database."""
        try:
            db.session.add(self)
            db.session.flush()
            if commit:
                db.session.commit()
            return self.id
        except IntegrityError as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[ProcurementData.create_row] IntegrityError: {str(e)}")
            logging.error(f"[ProcurementData.create_row] Full traceback: {exceptionstring}")
            raise
        except Exception as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[ProcurementData.create_row] Error: {str(e)}")
            logging.error(f"[ProcurementData.create_row] Full traceback: {exceptionstring}")
            raise

    def update_row(self, commit=True):
        """Commit changes made to an existing ProcurementData record."""
        try:
            self.updated_at = datetime.utcnow()
            db.session.add(self)
            if commit:
                db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[ProcurementData.update_row] IntegrityError: {str(e)}")
            logging.error(f"[ProcurementData.update_row] Full traceback: {exceptionstring}")
            raise
        except Exception as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[ProcurementData.update_row] Error: {str(e)}")
            logging.error(f"[ProcurementData.update_row] Full traceback: {exceptionstring}")
            raise

    def delete_row(self):
        """Delete this ProcurementData record from the database."""
        try:
            stmt = delete(ProcurementData).where(ProcurementData.id == self.id)
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
            logging.error(f"[ProcurementData.delete_row] IntegrityError: {str(e)}")
            logging.error(f"[ProcurementData.delete_row] Full traceback: {exceptionstring}")
            raise
        except Exception as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            error_type = type(e).__name__
            logging.error(f"[ProcurementData.delete_row] Error ({error_type}): {str(e)}")
            logging.error(f"[ProcurementData.delete_row] Full traceback: {exceptionstring}")
            raise

    @staticmethod
    def get_by_id(procurement_id):
        """Fetch a ProcurementData record safely by ID."""
        try:
            procurement = ProcurementData.query.get(procurement_id)
            return procurement
        except Exception:
            exceptionstring = traceback.format_exc()
            logging.error(f"[ProcurementData.get_by_id] Error: {exceptionstring}")
            return None

    @staticmethod
    def get_by_site_id(site_id):
        """Get procurement data for a specific site."""
        try:
            procurement = ProcurementData.query.filter_by(site_id=site_id).first()
            return procurement
        except Exception:
            exceptionstring = traceback.format_exc()
            logging.error(f"[ProcurementData.get_by_site_id] Error: {exceptionstring}")
            return None

