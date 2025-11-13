from datetime import datetime
from launchpad_api.db import db
import traceback
from sqlalchemy import UniqueConstraint

class Section(db.Model):
    __tablename__ = 'section'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section_name = db.Column(db.String(255), nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id',ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('section_name', 'page_id', name='uix_sectionname_pageid'),
    )
    # Relationship to Page model
    page = db.relationship('Page', backref=db.backref('sections', lazy=True))

    def __init__(self, section_name, page_id):
        self.section_name = section_name
        self.page_id = page_id

    def __repr__(self):
        return f"<Section(id={self.id}, section_name='{self.section_name}', page_id={self.page_id})>"

    # --- CRUD Operations ---

    def create_row(self,commit=True):
        """Insert a new Section record into the database."""
        try:
            db.session.add(self)
            if commit and not db.session.in_transaction():
                db.session.commit()
            return self.id
        except Exception:
            db.session.rollback()
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
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
        """Delete this Section record from the database."""
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
    def get_by_id(section_id):
        """Fetch a Section record safely by ID."""
        try:
            section = Section.query.get(section_id)
            return section
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None

    @staticmethod
    def get_by_pageid_and_sectionname(page_id,section_name):
        try:
            section = Section.query.filter(Section.page_id==page_id, Section.section_name==section_name).first()
            return section
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None
    @staticmethod
    def get_by_pageid(page_id):
        try:
            sections = Section.query.filter(Section.page_id==page_id).all()
            return sections
        except Exception:
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None
    
    @staticmethod
    def get_by_ids(section_ids):
        """Fetch Field records safely by multiple section IDs."""
        try:
            if not section_ids:
                return []

            sections = Section.query.filter(Section.id.in_(section_ids)).all()
            return sections
        except Exception:
            import traceback
            exceptionstring = traceback.format_exc()
            print(exceptionstring)
            return None
    
    def check_all_ids_exist(section_ids):
        """Fetch all sections by IDs and ensure they all exist."""
        try:
            if not section_ids:
                return [], False  # No IDs provided

            sections = Section.query.filter(Section.id.in_(section_ids)).all()
            
            found_ids = {s.id for s in sections}
            missing_ids = set(section_ids) - found_ids

            if missing_ids:
                # Some IDs do not exist
                return sections, False

            # All IDs exist
            return sections, True

        except Exception:
            import traceback
            print(traceback.format_exc())
            return None, False


