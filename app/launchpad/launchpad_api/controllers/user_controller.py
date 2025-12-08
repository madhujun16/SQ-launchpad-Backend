import connexion

from flask import jsonify, request
from launchpad_api.models.user_request import UserRequest  # noqa: E501
from launchpad_api import util
from launchpad_api.db_models.user import User
from launchpad_api.utils.messages import generic_message
from launchpad_api.utils import transform_data
from launchpad_api.utils.cookie_manager import decrypt_token
from launchpad_api.utils.common_functions import get_user_details


def user_delete(user_id):  # noqa: E501
    """Delete a user

     # noqa: E501

    :param user_id: 
    :type user_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}
    
    try:
        if not user_id:
            payload = {"message": "User ID is missing"}
            result = 400
            return jsonify(payload), result
        
        user = User.get_by_id(user_id)
        
        if not user:
            payload = {"message": "User not found"}
            result = 404
            return jsonify(payload), result
        
        deleted_id = user.delete_row()
        
        if deleted_id:
            payload = {"message": "User deleted successfully"}
            result = 200
        else:
            payload = {"message": "Unable to delete the user"}
            result = 400
    
    except Exception as error:
        print(error)
        result = 400
        payload = {"message": generic_message}
    
    return jsonify(payload), result


def user_get(id):  # noqa: E501
    """Get list of users

     # noqa: E501


    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    # This endpoint seems to be for getting users by some id parameter
    # Keeping original behavior for now as it's not clear what it should do
    return "get user api not implement yet"

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
    payload = {"message":generic_message}

    try:
        name = user_request.name
        email = user_request.emailid
        role = user_request.role

        user = User(name,email,role)

        response = user.create_row()
        
        if response:
            data = transform_data.transform_user(user)
            payload = {"message":"User Created Succesfully","data":data}
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
    request_json = None
    if connexion.request.is_json:
        request_json = connexion.request.get_json()
        user_request = UserRequest.from_dict(request_json)  # noqa: E501
    
    result = 400
    payload = {"message": generic_message}
    
    try:
        # Check if id is provided in request body (might be in JSON but not in model)
        user_id = None
        if request_json and 'id' in request_json:
            user_id = request_json.get('id')
        elif hasattr(user_request, 'id') and user_request.id:
            user_id = user_request.id
        
        if not user_id:
            payload = {"message": "User ID is required for update"}
            result = 400
            return jsonify(payload), result
        
        user = User.get_by_id(user_id)
        
        if not user:
            payload = {"message": "User not found"}
            result = 404
            return jsonify(payload), result
        
        # Update user fields
        if hasattr(user_request, 'name') and user_request.name:
            user.name = user_request.name
        if hasattr(user_request, 'emailid') and user_request.emailid:
            user.email = user_request.emailid
        if hasattr(user_request, 'role') and user_request.role is not None:
            user.role = user_request.role
        
        if user.update_row():
            data = transform_data.transform_user(user)
            payload = {"message": "User updated successfully", "data": data}
            result = 200
        else:
            payload = {"message": "User update failed"}
            result = 400
    
    except Exception as error:
        print(error)
        result = 400
        payload = {"message": generic_message}
    
    return jsonify(payload), result

def user_all_get():  # noqa: E501
    """Get list of users

     # noqa: E501


    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message":generic_message}
    
    try:
        users = User.get_all_users()

        if users:
            all_users = transform_data.transform_users(users)
            result = 200
            payload = {"data":all_users,"message":"User data successfully fetched"}
       
    except Exception as error:
        print(error)

    return jsonify(payload),result


def user_me_get():  # noqa: E501
    """Get current logged-in user info

     # noqa: E501

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 401
    payload = {"message": "Unauthorized"}
    
    try:
        token = request.cookies.get("session_id")
        if not token:
            return jsonify(payload), result
        
        email = decrypt_token(token)
        if not email:
            return jsonify(payload), result
        
        user_details = get_user_details(email)
        
        if user_details:
            result = 200
            payload = {"message": "User info fetched successfully", "data": user_details}
        else:
            result = 404
            payload = {"message": "User not found"}
    
    except Exception as error:
        print(error)
        result = 400
        payload = {"message": generic_message}
    
    return jsonify(payload), result


def user_by_id_get(user_id):  # noqa: E501
    """Get user by ID

     # noqa: E501

    :param user_id: 
    :type user_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}
    
    try:
        if not user_id:
            payload = {"message": "User ID is missing"}
            result = 400
            return jsonify(payload), result
        
        user = User.get_by_id(user_id)
        
        if user:
            data = transform_data.transform_user(user)
            result = 200
            payload = {"message": "User fetched successfully", "data": data}
        else:
            result = 404
            payload = {"message": "User not found"}
    
    except Exception as error:
        print(error)
        result = 400
        payload = {"message": generic_message}
    
    return jsonify(payload), result


def user_by_id_put(user_id, body):  # noqa: E501
    """Update user by ID

     # noqa: E501

    :param user_id: 
    :type user_id: int
    :param user_request: 
    :type user_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    user_request = body
    if connexion.request.is_json:
        user_request = UserRequest.from_dict(connexion.request.get_json())  # noqa: E501
    
    result = 400
    payload = {"message": generic_message}
    
    try:
        if not user_id:
            payload = {"message": "User ID is missing"}
            result = 400
            return jsonify(payload), result
        
        user = User.get_by_id(user_id)
        
        if not user:
            payload = {"message": "User not found"}
            result = 404
            return jsonify(payload), result
        
        # Update user fields
        if hasattr(user_request, 'name') and user_request.name:
            user.name = user_request.name
        if hasattr(user_request, 'emailid') and user_request.emailid:
            user.email = user_request.emailid
        if hasattr(user_request, 'role') and user_request.role is not None:
            user.role = user_request.role
        
        if user.update_row():
            data = transform_data.transform_user(user)
            payload = {"message": "User updated successfully", "data": data}
            result = 200
        else:
            payload = {"message": "User update failed"}
            result = 400
    
    except Exception as error:
        print(error)
        result = 400
        payload = {"message": generic_message}
    
    return jsonify(payload), result


def user_by_id_delete(user_id):  # noqa: E501
    """Delete user by ID

     # noqa: E501

    :param user_id: 
    :type user_id: int

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    result = 400
    payload = {"message": generic_message}
    
    try:
        if not user_id:
            payload = {"message": "User ID is missing"}
            result = 400
            return jsonify(payload), result
        
        user = User.get_by_id(user_id)
        
        if not user:
            payload = {"message": "User not found"}
            result = 404
            return jsonify(payload), result
        
        deleted_id = user.delete_row()
        
        if deleted_id:
            payload = {"message": "User deleted successfully"}
            result = 200
        else:
            payload = {"message": "Unable to delete the user"}
            result = 400
    
    except Exception as error:
        print(error)
        result = 400
        payload = {"message": generic_message}
    
    return jsonify(payload), result