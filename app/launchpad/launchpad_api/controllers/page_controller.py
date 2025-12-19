import connexion
import json
import traceback
import logging
from flask import jsonify
from ..models.page_request import PageRequest  # noqa: E501
from ..utils import messages ,transform_data
from datetime import datetime

from ..db_models.site import Site
from ..db_models.page import Page
from ..db_models.section import Section
from ..db import db
from ..db_models.fields import Field


def page_delete(page_id):  # noqa: E501
    """Delete a page

     # noqa: E501

    :param page_id: 
    :type page_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    return 'do some magic!'


def create_page_response(page, sections, fields):
    """
    Build a structured response for a page with its sections and fields.

    Args:
        page: Page model instance
        sections: list of Section model instances
        fields: list of Field model instances

    Returns:
        dict: Serialized page data including sections and their fields
    """
    # Transform page
    page_data = transform_data.transform_page(page)

    # Prepare mapping of section_id → fields
    section_fields_map = {}
    for field in fields or []:
        section_id = getattr(field, "section_id", None)
        if section_id not in section_fields_map:
            section_fields_map[section_id] = []
        section_fields_map[section_id].append(transform_data.transform_field(field))

    # Transform sections and attach their fields
    sections_data = []
    for section in sections or []:
        section_data = transform_data.transform_section(section)
        section_data["fields"] = section_fields_map.get(section_data["section_id"], [])
        sections_data.append(section_data)

    # Final structured page response
    page_data["sections"] = sections_data

    return page_data


def page_get(page_name, site_id):  # noqa: E501
    """Get list of pages

     # noqa: E501

    :param page_name: Name of the page to fetch sections for
    :type page_name: str
    :param site_id: 
    :type site_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """

    result = 400
    payload = {"message":messages.generic_message}

    try:
        logging.info(f"[page_get] Fetching page_name={page_name}, site_id={site_id}")
        
        page = Page.get_by_siteid_and_pagename(site_id,page_name)

        if not page:
            logging.warning(f"[page_get] Page not found: page_name={page_name}, site_id={site_id}")
            result = 400
            payload = {"message":"Invalid Page name or site"}
            return jsonify(payload),result
        
        logging.info(f"[page_get] Found page id={page.id}, fetching sections...")
        
        sections = Section.get_by_pageid(page.id)
        
        # Handle None (error) vs empty list (no sections yet - valid state)
        if sections is None:
            logging.error(f"[page_get] Error fetching sections for page_id={page.id}")
            result = 500
            payload = {"message":"Error fetching sections"}
            return jsonify(payload),result
        
        logging.info(f"[page_get] Found {len(sections)} sections for page_id={page.id}")
        
        # If no sections, return page with empty sections array (valid state)
        if not sections:
            page_data = transform_data.transform_page(page)
            page_data["sections"] = []
            payload = {"message":"Succesfully fetched the data","data":page_data}
            result = 200
            return jsonify(payload),result

        section_ids = [section.id for section in sections]
        logging.info(f"[page_get] Fetching fields for section_ids={section_ids}")

        fields = Field.get_by_section_ids(section_ids)
        
        # Handle None (error) vs empty list (no fields yet - valid state)
        if fields is None:
            logging.error(f"[page_get] Error fetching fields for section_ids={section_ids}")
            result = 500
            payload = {"message":"Error fetching fields"}
            return jsonify(payload),result
        
        logging.info(f"[page_get] Found {len(fields)} fields across {len(sections)} sections")
        
        # Even if no fields, return the page with sections (fields can be empty arrays)
        page_data = create_page_response(page,sections,fields or [])

        payload = {"message":"Succesfully fetched the data","data":page_data}
        result = 200

        
    except Exception as error:
        logging.error(f"[page_get] Exception: {error}")
        logging.error(traceback.format_exc())
        result = 500
        payload = {"message":messages.generic_message}
        print(traceback.format_exc())

    return jsonify(payload),result

# """
#     In the page_post , i am making following assumptions
#     1. It doesn't have any sections yet
#     2. sections have no fields yet
#     3. There may not be site created as well
#     Actions which i need to perform
#     1. if site_id is None , need to create a site (check the name) - required or not
#     2. create a page (check the name within the same site) - required or not
#     3. create sections (check the section within the page) - required or not
#     4 create fields under sections (check the field within the page (required or not))

# """

def create_site(status):
    new_site = Site(status)
    site_id = new_site.create_row(commit=False)    
    return site_id
            

def create_page(page_name,site_id):
    new_page = Page(page_name,site_id)
    page_id = new_page.create_row(commit=False)
    return page_id

def create_section(section_name,page_id):
    new_section = Section(section_name,page_id)
    section_id = new_section.create_row(commit=False)

    return section_id


def page_post(body):  # noqa: E501
    """Create a new page

     # noqa: E501

    :param page_request: 
    :type page_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    page_request = body
    if connexion.request.is_json:
        page_request = PageRequest.from_dict(connexion.request.get_json())  # noqa: E501

    result = 400
    payload = {"message":messages.generic_message}
    data = {}
    try:
        site_id = page_request.site_id
        status = page_request.status
        # check if site exists , if not create a site
        if not site_id:
            site_id = create_site(status)
        

        if not site_id:
            result = 400
            payload = {"message":"Invalid site details"}
            return jsonify(payload),result

        # create a page
        page_name = page_request.page_name

        page_id = create_page(page_name,site_id)

        if not page_id:
            result = 400
            payload = {"message":"Invalid page details"}
            return jsonify(payload),result
        
        data = {
            "site_id":site_id,
            "page_id":page_id,
            "page_name":page_name,
            "sections":[]
        }

        sections = page_request.sections

        section_details = []
        for section in sections:
            section_detail = {}
            section_name = section.section_name
            section_id = create_section(section_name,page_id)
            
            if not section_id:
                result = 400
                payload = {"message":f"Error creating section {section_name}"}
                return jsonify(payload),result
            
            section_detail = {"section_id":section_id,"section_name":section_name,"fields":[]}
            fields = section.fields

            all_fields = []
            for field in fields:
                field_name = field.field_name
                field_value = field.field_value

                new_field = {"field_name":field_name,"field_value":json.dumps(field_value),"section_id":section_id}
                all_fields.append(new_field)


            field_details = Field.create_multiple(all_fields)
            
            if field_details is None:
                # IntegrityError → duplicate field name in section
                payload = {"message": f"Duplicate field in section '{section_name}'. Each field_name must be unique per section."}
                result = 400
                return payload,result
            elif field_details is False:
                payload = {"message": f"Error inserting fields for section {section_name}"}
                result = 400
                return payload,result
            
            section_detail['fields'] = transform_data.transform_fields(field_details)
        
            section_details.append(section_detail)

        data["sections"] = section_details
        db.session.commit()
        result = 200
        payload = {"message":"Page saved successfully","data":data}

    except Exception as error:
        db.session.rollback()
        result = 400
        payload = {"message":messages.generic_message}
        print(traceback.format_exc())

    return jsonify(payload),result

def page_put(body):  # noqa: E501
    """Update an existing page

     # noqa: E501

    :param page_request: 
    :type page_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    page_request = body
    if connexion.request.is_json:
        page_request = PageRequest.from_dict(connexion.request.get_json())  # noqa: E501
    
    try:
        site_id = page_request.site_id
        status = page_request.status
       
    
        if not site_id:
            result = 400
            payload = {"message":"Site ID is missing"}
            return jsonify(payload),result
        
        
        # update status in the site table
        site = Site.get_by_id(site_id)

        if not site:
            result = 400
            payload = {"message":"Invalid Site ID"}
            return jsonify(payload),result

        site.status = status
        site.updated_at = datetime.utcnow()
        site_updated  = site.update_row(False)

        if not site_updated:
            result = 400
            payload = {"message":"Unable to update the status of the site"}
            return jsonify(payload),result

        
        page_id = page_request.id

        if not page_id:
            result = 400
            payload = {"message":"Page ID is missing"}
            return jsonify(payload),result
        
        page = Page.get_by_id(page_id)

        if not page:
            result = 400
            payload = {"message":"Invalid Page ID"}
            return jsonify(payload),result

        page.updated_at = datetime.utcnow()
        page.update_row(False) 
        
        
        sections = page_request.sections       
        for section in sections:
            section_id = section.section_id
            section_detail = Section.get_by_id(section_id)

            if not section_detail:
                result = 400
                payload = {"message":"Invalid Section ID"}
                return jsonify(payload),result

            section_detail.updated_at = datetime.utcnow()
            section_detail.update_row(False)
            fields = section.fields
           
            for field in fields:
                field_id = field.field_id
                field_detail = Field.get_by_id(field_id)
                
                if not field_detail:
                    result = 400
                    payload = {"message":"Invalid Field ID"}
                    return jsonify(payload),result
                
                field_detail.field_value = field.field_value
                field_detail.update_row(False)
                
        db.session.commit()
        result = 200
        payload = {"message":"Page updated successfully"}

    except Exception as error:
        db.session.rollback()
        result = 400
        payload = {"message":messages.generic_message}
        print(traceback.format_exc())

    return jsonify(payload),result
