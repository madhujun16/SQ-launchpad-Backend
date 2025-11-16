import unittest

from flask import json

from launchpad_api.models.generate_upload_url_post_request import GenerateUploadUrlPostRequest  # noqa: E501
from launchpad_api.test import BaseTestCase


class TestUtilityController(BaseTestCase):
    """UtilityController integration test stubs"""

    def test_generate_upload_url_post(self):
        """Test case for generate_upload_url_post

        generate a signed url to upload logo
        """
        generate_upload_url_post_request = launchpad_api.GenerateUploadUrlPostRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'cookieAuth': 'special-key',
        }
        response = self.client.open(
            '/api/generate-upload-url',
            method='POST',
            headers=headers,
            data=json.dumps(generate_upload_url_post_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
