import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from launchpad_api.models.site_request import SiteRequest  # noqa: E501
from launchpad_api import util


def site_delete(site_id):  # noqa: E501
    """Delete a site

     # noqa: E501

    :param site_id: 
    :type site_id: str

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    return 'do some magic!'


def site_get():  # noqa: E501
    """Get list of sites

     # noqa: E501


    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    return 'do some magic!'


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
    return 'do some magic!'


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
    return 'do some magic!'
