import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from launchpad_api.models.user_request import UserRequest  # noqa: E501
from launchpad_api import util


def user_delete(user_id):  # noqa: E501
    """Delete a user

     # noqa: E501

    :param user_id: 
    :type user_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    return 'do some magic!'


def user_get():  # noqa: E501
    """Get list of users

     # noqa: E501


    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    return 'do some magic!'


def user_post(body):  # noqa: E501
    """Create a new user

     # noqa: E501

    :param user_request: 
    :type user_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    user_request = body
    if connexion.request.is_json:
        user_request = UserRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def user_put(body):  # noqa: E501
    """Update an existing user

     # noqa: E501

    :param user_request: 
    :type user_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    user_request = body
    if connexion.request.is_json:
        user_request = UserRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
