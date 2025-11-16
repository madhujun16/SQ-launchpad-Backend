import connexion
import logging
from google.cloud import storage
from launchpad_api.models.generate_upload_url_post_request import GenerateUploadUrlPostRequest  # noqa: E501
from launchpad_api import util
from launchpad_api.utils import messages
from flask import jsonify
import datetime


def generate_upload_url_post(body):  # noqa: E501
    """generate a signed url to upload logo

     # noqa: E501

    :param generate_upload_url_post_request: 
    :type generate_upload_url_post_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    generate_upload_url_post_request = body
    if connexion.request.is_json:
        generate_upload_url_post_request = GenerateUploadUrlPostRequest.from_dict(connexion.request.get_json())  # noqa: E501
    
    result = 400
    payload = {"message":messages.generic_message}

    try:
        key = generate_upload_url_post_request.data_identifier
        storage_client = storage.Client()
        bucket = storage_client.bucket("launchpad_logo")
        blob_name = f"{key}.svg"
        blob = bucket.blob(blob_name)

        upload_url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=15),
            method="PUT",  # allows upload via HTTP PUT
            content_type="image/png",  # match frontend upload type
            )
        
        public_url = f"https://storage.googleapis.com/{bucket.name}/{blob_name}"

        payload = {"message":"upload data","data":{"upload_url": upload_url,
                    "public_url": public_url}}
        
        result = 200
    except Exception as error:
        logging.info(error)
        print(error)
        result = 400
        payload = {"message":messages.generic_message}
    return jsonify(payload),result
