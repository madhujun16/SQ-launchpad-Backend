from datetime import datetime
from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import IntegrityError
from ..db import db
import traceback

class Field(db.Model):
    __tablename__ = 'field'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    field_name = db.Column(db.String(255), nullable=False)
    field_value = db.Column(db.JSON, nullable=True)  # stores JSON data
    section_id = db.Column(db.Integer, db.ForeignKey('section.id',ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('field_name', 'section_id', name='uix_fieldname_sectionid'),
    )
    # Relationship to Section model
    section = db.relationship('Section', backref=db.backref('fields', lazy=True))

    def __init__(self, field_name, field_value, section_id):
        self.field_name = field_name
        self.field_value = field_value
        self.section_id = section_id

    def __repr__(self):
        return f"<Field(id={self.id}, field_name='{self.field_name}', section_id={self.section_id})>"

    # --- CRUD operations ---
    def create_row(self,commit=True):
        """Create a new Field record."""
        try:
            db.session.add(self)
            if commit and not db.session.in_transaction():
                db.session.commit()
            return self.id

        except IntegrityError as e:
            db.session.rollback()
            print(f"❌ Duplicate entry for field_name='{self.field_name}' in section_id={self.section_id}")
            return None  # Duplicate key

        except Exception:
            db.session.rollback()
            print(traceback.format_exc())
            return False
    
    @staticmethod
    def create_multiple(data_list):
        """
        Create multiple Field records from a list of dictionaries.
        :param data_list: List of dicts, e.g. 
                        [{"field_name": "email", "field_value": {...}, "section_id": 1}, ...]
        :return: List of created IDs, None if duplicates, or False if general error
        """
        try:
            # Convert each dict to a Field model instance
            rows = [Field(**data) for data in data_list]

            db.session.add_all(rows)
            db.session.commit()

            return rows

        except IntegrityError as e:
            db.session.rollback()
            print("❌ IntegrityError: Duplicate (field_name, section_id) found.")
            print(f"Details: {str(e.orig)}")
            return None

        except Exception:
            db.session.rollback()
            print(traceback.format_exc())
            return False

    def update_row(self,commit=True):
        """Commit changes made to an existing Site record."""
        try:
            db.session.add(self)
            if commit:
                db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return False

    def delete_row(self):
        """Delete this Field record."""
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
    def get_by_id(field_id):
        """Fetch a Field record safely by ID."""
        try:
            field = Field.query.get(field_id)
            return field
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None
        
    @staticmethod
    def get_by_fielid_and_sectionid(field_id,section_id):
        """Fetch a Field record safely by ID."""
        try:
            field = Field.query.filter(Field.id==field_id, Field.section_id==section_id).first()
            return field
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None
        
    
    @staticmethod
    def get_by_section_ids(section_ids):
        """Fetch Field records safely by multiple section IDs."""
        try:
            if not section_ids:
                return []

            fields = Field.query.filter(Field.section_id.in_(section_ids)).all()
            return fields
        except Exception:
            import traceback
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None

    def check_all_ids_exist(field_ids):
        """Fetch all sections by IDs and ensure they all exist."""
        try:
            if not field_ids:
                return [], False  # No IDs provided

            fields = Field.query.filter(Field.id.in_(field_ids)).all()
            
            found_ids = {s.id for s in fields}
            missing_ids = set(field_ids) - found_ids

            if missing_ids:
                # Some IDs do not exist
                return fields, False

            # All IDs exist
            return fields, True

        except Exception:
            import traceback
            print(traceback.format_exc())
            return None, False

