import unittest

from flask import json

from models.user_request import UserRequest  # noqa: E501
from test import BaseTestCase


class TestUserController(BaseTestCase):
    """UserController integration test stubs"""

    def test_user_delete(self):
        """Test case for user_delete

        Delete a user
        """
        query_string = [('user_id', 56)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/user',
            method='DELETE',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_user_get(self):
        """Test case for user_get

        Get list of users
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/user',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_user_post(self):
        """Test case for user_post

        Create a new user
        """
        user_request = {"roles":["admin","editor"],"name":"John Doe","emailid":"john.doe@example.com"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/user',
            method='POST',
            headers=headers,
            data=json.dumps(user_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_user_put(self):
        """Test case for user_put

        Update an existing user
        """
        user_request = {"roles":["admin","editor"],"name":"John Doe","emailid":"john.doe@example.com"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/user',
            method='PUT',
            headers=headers,
            data=json.dumps(user_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
