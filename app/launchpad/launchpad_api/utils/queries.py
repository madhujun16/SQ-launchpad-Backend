from ..db import db
from sqlalchemy.orm import aliased
from ..db_models.site import Site
from ..db_models.page import Page
from ..db_models.section import Section
from ..db_models.fields import Field
import traceback
import logging


def get_all_site_details(siteid=None):


    p = aliased(Page)
    sec = aliased(Section)
    f = aliased(Field)
    try:

        if siteid:
            query = (
                db.session.query(
                    Site.id,
                    Site.status,
                    f.field_name,
                    f.field_value
                )
                .outerjoin(
                    p,
                    (p.site_id == Site.id) &
                    (p.page_name == 'site_study')
                )
                .outerjoin(
                    sec,
                    (sec.page_id == p.id) &
                    (sec.section_name == 'general_info')
                )
                .outerjoin(
                    f,
                    f.section_id == sec.id
                )
            ).filter(Site.id == siteid)

        else:
            query = (
            db.session.query(
                Site.id,
                Site.status,
                f.field_name,
                f.field_value
            )
            .outerjoin(
                p,
                (p.site_id == Site.id) &
                (p.page_name == 'site_study')
            )
            .outerjoin(
                sec,
                (sec.page_id == p.id) &
                (sec.section_name == 'general_info')
            )
            .outerjoin(
                f,
                f.section_id == sec.id
            )
        )

        result = query.all()
        return result

    except Exception as error:
        logging.error("Failed to create database:\n%s", traceback.format_exc())
        return None