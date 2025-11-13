from launchpad_api.db import db
from datetime import datetime
import traceback
from sqlalchemy.dialects.postgresql import JSON

class RolePermissionMap(db.Model):
    __tablename__ = "role_permission_map"

    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(255), unique=True, nullable=False)
    permissions = db.Column(JSON, nullable=False, default={})

    def __init__(self, role_name, permissions=None):
        self.role_name = role_name
        self.permissions = permissions or {}

    def __repr__(self):
        return f"<RolePermissionMap(role_id={self.role_id}, role_name='{self.role_name}')>"

    # --- CRUD Operations ---

    def create_row(self):
        """Insert a new role permission map."""
        try:
            db.session.add(self)
            db.session.commit()
            return self.role_id
        except Exception:
            db.session.rollback()
            print(traceback.format_exc())
            return False

    def update_row(self):
        """Commit updates made to this role."""
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            print(traceback.format_exc())
            return False

    def delete_row(self):
        """Delete this role permission entry."""
        try:
            db.session.delete(self)
            db.session.commit()
            return self.role_id
        except Exception:
            db.session.rollback()
            print(traceback.format_exc())
            return False

    @staticmethod
    def get_by_id(role_id):
        """Fetch a role permission record by ID."""
        try:
            return RolePermissionMap.query.get(role_id)
        except Exception:
            print(traceback.format_exc())
            return None

    @staticmethod
    def get_by_role_name(role_name):
        """Fetch a role permission record by name."""
        try:
            return RolePermissionMap.query.filter(RolePermissionMap.role_name==role_name).first()
        except Exception:
            print(traceback.format_exc())
            return None

    @staticmethod
    def get_all():
        """Fetch all role permission records."""
        try:
            return RolePermissionMap.query.all()
        except Exception:
            print(traceback.format_exc())
            return None
