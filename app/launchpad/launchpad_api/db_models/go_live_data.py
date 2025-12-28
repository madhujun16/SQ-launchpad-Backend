from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete
import logging
from ..db import db
import traceback

class GoLiveData(db.Model):
    __tablename__ = 'go_live_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id', ondelete='CASCADE'), nullable=False, unique=True)
    status = db.Column(db.String(50), nullable=False, default='offline')  # 'live', 'offline', 'postponed'
    go_live_date = db.Column(db.DateTime, nullable=True)
    signed_off_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    site = db.relationship('Site', backref=db.backref('go_live_data', uselist=False))
    signer = db.relationship('User', backref='go_live_signoffs')

    def __init__(self, site_id, status='offline', go_live_date=None, signed_off_by=None, notes=None):
        self.site_id = site_id
        self.status = status
        self.go_live_date = go_live_date
        self.signed_off_by = signed_off_by
        self.notes = notes

    def __repr__(self):
        return f"<GoLiveData(id={self.id}, site_id={self.site_id}, status='{self.status}')>"

    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            'id': str(self.id),
            'site_id': str(self.site_id),
            'status': self.status,
            'go_live_date': self.go_live_date.isoformat() if self.go_live_date else None,
            'signed_off_by': str(self.signed_off_by) if self.signed_off_by else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def create_row(self, commit=True):
        """Insert a new GoLiveData record into the database."""
        try:
            db.session.add(self)
            db.session.flush()
            if commit:
                db.session.commit()
            return self.id
        except IntegrityError as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[GoLiveData.create_row] IntegrityError: {str(e)}")
            logging.error(f"[GoLiveData.create_row] Full traceback: {exceptionstring}")
            raise
        except Exception as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[GoLiveData.create_row] Error: {str(e)}")
            logging.error(f"[GoLiveData.create_row] Full traceback: {exceptionstring}")
            raise

    def update_row(self, commit=True):
        """Commit changes made to an existing GoLiveData record."""
        try:
            self.updated_at = datetime.utcnow()
            db.session.add(self)
            if commit:
                db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[GoLiveData.update_row] IntegrityError: {str(e)}")
            logging.error(f"[GoLiveData.update_row] Full traceback: {exceptionstring}")
            raise
        except Exception as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            logging.error(f"[GoLiveData.update_row] Error: {str(e)}")
            logging.error(f"[GoLiveData.update_row] Full traceback: {exceptionstring}")
            raise

    def delete_row(self):
        """Delete this GoLiveData record from the database."""
        try:
            # Use SQLAlchemy delete statement for maximum reliability
            stmt = delete(GoLiveData).where(GoLiveData.id == self.id)
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
            logging.error(f"[GoLiveData.delete_row] IntegrityError: {str(e)}")
            logging.error(f"[GoLiveData.delete_row] Full traceback: {exceptionstring}")
            raise
        except Exception as e:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            error_type = type(e).__name__
            logging.error(f"[GoLiveData.delete_row] Error ({error_type}): {str(e)}")
            logging.error(f"[GoLiveData.delete_row] Full traceback: {exceptionstring}")
            raise

    @staticmethod
    def get_by_site_id(site_id):
        """Get go live data for a specific site."""
        try:
            go_live = GoLiveData.query.filter_by(site_id=site_id).first()
            return go_live
        except Exception:
            exceptionstring = traceback.format_exc()
            logging.error(f"[GoLiveData.get_by_site_id] Error: {exceptionstring}")
            return None

    @staticmethod
    def get_by_id(go_live_id):
        """Fetch a GoLiveData record safely by ID."""
        try:
            go_live = GoLiveData.query.get(go_live_id)
            return go_live
        except Exception:
            exceptionstring = traceback.format_exc()
            logging.error(f"[GoLiveData.get_by_id] Error: {exceptionstring}")
            return None

