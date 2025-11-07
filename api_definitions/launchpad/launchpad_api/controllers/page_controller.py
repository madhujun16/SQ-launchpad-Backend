import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from launchpad_api.models.page_request import PageRequest  # noqa: E501
from launchpad_api import util


def page_delete(page_id):  # noqa: E501
    """Delete a page

     # noqa: E501

    :param page_id: 
    :type page_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    return 'do some magic!'


def page_get(page_name, site_id):  # noqa: E501
    """Get list of pages

     # noqa: E501

    :param page_name: Name of the page to fetch sections for
    :type page_name: str
    :param site_id: 
    :type site_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    return 'do some magic!'


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
    return 'do some magic!'


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
    return 'do some magic!'
