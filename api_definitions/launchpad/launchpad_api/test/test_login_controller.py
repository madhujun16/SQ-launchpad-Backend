import unittest

from flask import json

from launchpad_api.models.login_request import LoginRequest  # noqa: E501
from launchpad_api.test import BaseTestCase


class TestLoginController(BaseTestCase):
    """LoginController integration test stubs"""

    def test_login_post(self):
        """Test case for login_post

        Login and set auth cookie
        """
        login_request = {"password":"password","username":"username"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/login',
            method='POST',
            headers=headers,
            data=json.dumps(login_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
