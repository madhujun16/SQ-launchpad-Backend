import connexion
from flask import jsonify
import logging
from ..models.site_request import SiteRequest  # noqa: E501
from ..utils.messages import generic_message
from ..db_models.site import Site
from ..utils import transform_data
from ..utils.queries import get_all_site_details
from collections import defaultdict
import json

def site_delete(site_id):  # noqa: E501
    """Delete a site

     # noqa: E501

    :param site_id: 
    :type site_id: str

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message":generic_message}

    try:
        if not site_id:
            payload = {"message":"Site ID is missing"}
            result = 400
            return jsonify(payload),result
        
        site = Site.delete_by_id(site_id)

        if site:
            payload = {"message": "Site deleted successfully"}
            result = 200
        else:
            payload = {"message": "Unable to delete the site"}
            result = 400

    except Exception as error:
        print(error)
        result = 400
        payload = {"message":generic_message}

    return jsonify(payload),result

def site_get(id):  # noqa: E501
    """Get list of sites

     # noqa: E501


    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    
    return "site get api not implement yet"


def site_post(body):  # noqa: E501
    """Create a new site

     # noqa: E501

    :param site_request: 
    :type site_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    site_request = body
    if connexion.request.is_json:
        site_request = SiteRequest.from_dict(connexion.request.get_json())  # noqa: E501

    result = 400
    payload = {"message":generic_message}

    try:
        name = site_request.name
        status = site_request.status
        site = Site(name,status)
        
        response = site.create_row()

        if response:
            payload = {"message":"Site Created Succesfully"}
            result = 200
        else:
            payload = {"message":"Site creation failed"}
            result = 400

    except Exception as error:
        print(error)
        result = 400
        payload = {"message":generic_message}


    return jsonify(payload),result


def site_put(body):  # noqa: E501
    """Update an existing site

     # noqa: E501

    :param site_request: 
    :type site_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    site_request = body
    if connexion.request.is_json:
        site_request = SiteRequest.from_dict(connexion.request.get_json())  # noqa: E501
    
    result = 400
    payload = {"message":generic_message}

    try:
        name = site_request.name
        id = site_request.id
        status = site_request.status

        if not id:
            payload = {"message":"Invalid Site ID"}
            result = 400
            return jsonify(payload),result
        
        site = Site.get_by_id(id)

        if site:
            site.name = name
            site.status = status
            Site.update_row(site)

        else:
            payload = {"message":"Invalid Site ID"}
            result = 400
        
    except Exception as error:
        print(error)
        result = 400
        payload = {"message":generic_message}

    return jsonify(payload),result

def site_all_get():  # noqa: E501
    """Get list of sites

     # noqa: E501


    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message":generic_message}

    try:
        all_sites = get_all_site_details()
        sites = defaultdict(dict)

        if all_sites is None:
            payload = {"message":"Unable to fetch sites"}
            result = 400
            return jsonify(payload),result
        
        for site in all_sites:
            site_id = site.id
            _site = sites.get(site_id, {})
            _site['site_id'] = site_id
            _site['status'] = site.status
            if site.field_name:
                _site[site.field_name] = json.loads(site.field_value)

            sites[site_id] = _site
        
        payload = {"data":list(sites.values()),"message":"Succesfully fetched sites"}
        result = 200
            

    except Exception as error:
        logging.info(error)
        print(error)
        result = 400
        payload = {"message":generic_message}
    return jsonify(payload),result