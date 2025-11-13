import json
from google.cloud import secretmanager
from launchpad_api.db_models.user import User
from launchpad_api.db_models.role_permission import RolePermissionMap
import traceback

def get_pii_encryption_key_from_secrets(secret_version_path):
    if secret_version_path is None:
        return None
    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version({"name": secret_version_path})
    payload = response.payload.data.decode('UTF-8')
    try:
        return json.loads(payload)
    except:
        return payload
    

def get_user_details(emaild):
    _user = {}
    try:
        user = User.get_by_email(emaild)

        if not user:
            return None  # Return early if no user found

        user_permissions = RolePermissionMap.get_by_id(user.role)

        if user_permissions:
            _user = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user_permissions.role_name,
                "permissions": user_permissions.permissions
            }

        return _user or None  # Return None if permissions not found

    except Exception as error:
        print("Error in get_user_details:", error)
        print(traceback.format_exc())
        return None
