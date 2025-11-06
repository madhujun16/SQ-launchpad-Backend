import connexion

from flask import jsonify
from launchpad_api.models.user_request import UserRequest  # noqa: E501
from launchpad_api import util
from db_models.user import User
from utils.messages import message



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

    result = 400
    payload = {"message":message.get("generic_message")}
    try:
        users = User.get_all_users()

        if users:
            result = 200
            payload = {"data":users,"message":"User data successfully fetched"}
       
    except Exception as error:
        print(error)

    return jsonify(payload),result

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
    
    result = 400
    payload = {"message":message.get("generic_message")}
    try:
        name = user_request.name
        email = user_request.emailid
        roles = user_request.roles

        user = User(name,email)

        response = user.create_row()
        
        if response:
            payload = {"message":"User Created Succesfully"}
            result = 200
        else:
            payload = {"message":"User creation failed"}
            result = 400

    except Exception as error:
        print(error)
    return jsonify(payload),result


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
