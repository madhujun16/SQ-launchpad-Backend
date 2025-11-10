from datetime import datetime
from launchpad_api.db import db
import traceback

class Organization(db.Model):
    __tablename__ = 'organization'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False,unique=True)
    description = db.Column(db.Text, nullable=True)
    sector = db.Column(db.String(100), nullable=False)
    unit_code = db.Column(db.String(50), nullable=False, unique=True)
    organization_logo = db.Column(db.String(512), nullable=True)  # store logo URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name, description=None, sector=None, unit_code=None, organization_logo=None):
        self.name = name
        self.description = description
        self.sector = sector
        self.unit_code = unit_code
        self.organization_logo = organization_logo

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', sector='{self.sector}')>"

    def create_row(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self.name
        except Exception:
            exceptionstring = traceback.format_exc()
            db.session.rollback()
            print(exceptionstring)
            return False

    def update_row(self):
        try:
            db.session.commit()
            return True
        except Exception:
            exceptionstring = traceback.format_exc()
            db.session.rollback()
            print(exceptionstring)
            return False

    def delete_row(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return self.id
        except Exception:
            exceptionstring = traceback.format_exc()
            db.session.rollback()
            print(exceptionstring)
            return False

    @staticmethod
    def get_by_id(org_id):
        """Fetch an organization record safely by ID."""
        try:
            org = Organization.query.get(org_id)
            return org
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None
