import json
import os
import logging
from ..db_models.user import User
from ..db_models.role_permission import RolePermissionMap
import traceback

def get_pii_encryption_key_from_secrets(secret_version_path):
    """Get secret from Google Cloud Secret Manager, with fallback to environment variables for local dev."""
    if secret_version_path is None:
        return None
    
    # Try to use Google Cloud Secret Manager
    try:
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version({"name": secret_version_path})
        payload = response.payload.data.decode('UTF-8')
        try:
            return json.loads(payload)
        except:
            return payload
    except Exception as e:
        # Fallback to environment variables for local development
        logging.warning(f"Could not access Secret Manager ({e}). Falling back to environment variables.")
        
        # Map secret paths to environment variable names
        env_var_map = {
            "certificate": "DB_SSL_CERT",
            "key": "DB_SSL_KEY", 
            "ca": "DB_SSL_CA",
            "db_credentials": None  # Special handling below
        }
        
        # Extract secret name from path (e.g., "launchpad_mysql_certificate" from full path)
        secret_name = None
        if "launchpad_mysql_certificate" in secret_version_path:
            secret_name = "certificate"
        elif "launchpad_mysql_key" in secret_version_path:
            secret_name = "key"
        elif "launchpad_mysql_ca" in secret_version_path:
            secret_name = "ca"
        elif "launchpad_db_credentials" in secret_version_path:
            # Return DB credentials from env vars
            return {
                "username": os.getenv("DB_USERNAME", "root"),
                "password": os.getenv("DB_PASSWORD", ""),
                "server_ip": os.getenv("DB_HOST", "localhost"),
                "database": os.getenv("DB_NAME", "launchpad_db")
            }
        
        if secret_name and env_var_map.get(secret_name):
            env_var = env_var_map[secret_name]
            value = os.getenv(env_var)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
        
        return None
    

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
