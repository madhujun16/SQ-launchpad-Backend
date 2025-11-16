import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from launchpad_api.models.generate_upload_url_post_request import GenerateUploadUrlPostRequest  # noqa: E501
from launchpad_api import util


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
    return 'do some magic!'
