import json
from google.cloud import secretmanager

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