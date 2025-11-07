import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from launchpad_api.models.section_request import SectionRequest  # noqa: E501
from launchpad_api import util


def section_delete(section_id):  # noqa: E501
    """Delete a section

     # noqa: E501

    :param section_id: 
    :type section_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    return 'do some magic!'


def section_get(page_id, section_name=None):  # noqa: E501
    """Get list of sections or selected section

     # noqa: E501

    :param page_id: 
    :type page_id: int
    :param section_name: Name of the section to fetch
    :type section_name: str

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    return 'do some magic!'


def section_post(body):  # noqa: E501
    """Create a new section

     # noqa: E501

    :param section_request: 
    :type section_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    section_request = body
    if connexion.request.is_json:
        section_request = SectionRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def section_put(body):  # noqa: E501
    """Update an existing section

     # noqa: E501

    :param section_request: 
    :type section_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    section_request = body
    if connexion.request.is_json:
        section_request = SectionRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
