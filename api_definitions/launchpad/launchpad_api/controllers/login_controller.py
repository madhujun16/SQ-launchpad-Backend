import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from launchpad_api.models.login_request import LoginRequest  # noqa: E501
from launchpad_api import util


def login_post(body):  # noqa: E501
    """Login and set auth cookie

     # noqa: E501

    :param login_request: 
    :type login_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    login_request = body
    if connexion.request.is_json:
        login_request = LoginRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
