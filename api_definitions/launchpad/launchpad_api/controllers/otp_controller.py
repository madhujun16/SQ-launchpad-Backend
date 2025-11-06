import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from launchpad_api.models.login_request import LoginRequest  # noqa: E501
from launchpad_api.models.otp_request import OtpRequest  # noqa: E501
from launchpad_api import util


def send_otp_post(body):  # noqa: E501
    """send otp

     # noqa: E501

    :param otp_request: 
    :type otp_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    otp_request = body
    if connexion.request.is_json:
        otp_request = OtpRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def verify_otp_post(body):  # noqa: E501
    """verify otp

     # noqa: E501

    :param login_request: 
    :type login_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    login_request = body
    if connexion.request.is_json:
        login_request = LoginRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
