import connexion
from typing import Dict
from typing import Tuple
from typing import Union
from flask import jsonify, make_response

from launchpad_api.models.login_request import LoginRequest  # noqa: E501
from launchpad_api import util
from launchpad_api.utils.messages import generic_message


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


def logout_post():  # noqa: E501
    """Logout user

     # noqa: E501

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    try:
        resp = make_response(jsonify({"message": "Logout successful"}))
        # Clear the session cookie by setting it with max_age=0
        resp.set_cookie("session_id", "", httponly=True, secure=False, samesite="Lax", max_age=0)
        return resp
    except Exception as error:
        print(error)
        return jsonify({"message": generic_message}), 400
