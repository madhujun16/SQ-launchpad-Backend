import unittest

from flask import json

from launchpad_api.models.otp_request import OtpRequest  # noqa: E501
from launchpad_api.test import BaseTestCase


class TestOtpController(BaseTestCase):
    """OtpController integration test stubs"""

    def test_send_otp_post(self):
        """Test case for send_otp_post

        send otp
        """
        otp_request = {"email":"email"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/send/otp',
            method='POST',
            headers=headers,
            data=json.dumps(otp_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
