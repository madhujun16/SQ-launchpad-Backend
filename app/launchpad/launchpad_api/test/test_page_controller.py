import unittest

from flask import json

from launchpad_api.models.page_request import PageRequest  # noqa: E501
from launchpad_api.test import BaseTestCase


class TestPageController(BaseTestCase):
    """PageController integration test stubs"""

    def test_page_delete(self):
        """Test case for page_delete

        Delete a page
        """
        query_string = [('page_id', 56)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/page',
            method='DELETE',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_page_get(self):
        """Test case for page_get

        Get list of pages
        """
        query_string = [('page_name', 'page_name_example'),
                        ('site_id', 56)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/page',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_page_post(self):
        """Test case for page_post

        Create a new page
        """
        page_request = {"page_name":"Home Page","site_id":1,"id":0}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/page',
            method='POST',
            headers=headers,
            data=json.dumps(page_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_page_put(self):
        """Test case for page_put

        Update an existing page
        """
        page_request = {"page_name":"Home Page","site_id":1,"id":0}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/page',
            method='PUT',
            headers=headers,
            data=json.dumps(page_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
