import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from launchpad_api.models.organization_request import OrganizationRequest  # noqa: E501
from launchpad_api import util


def organization_delete(organization_id):  # noqa: E501
    """Delete an organization

     # noqa: E501

    :param organization_id: 
    :type organization_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    return 'do some magic!'


def organization_get(organization_id=None):  # noqa: E501
    """Get list of organizations

     # noqa: E501

    :param organization_id: 
    :type organization_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    return 'do some magic!'


def organization_post(body):  # noqa: E501
    """Create a new organization

     # noqa: E501

    :param organization_request: 
    :type organization_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    organization_request = body
    if connexion.request.is_json:
        organization_request = OrganizationRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def organization_put(body):  # noqa: E501
    """Update an existing organization

     # noqa: E501

    :param organization_request: 
    :type organization_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    organization_request = body
    if connexion.request.is_json:
        organization_request = OrganizationRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
