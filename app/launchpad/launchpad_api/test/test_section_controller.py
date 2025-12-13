import unittest

from flask import json

from models.section_request import SectionRequest  # noqa: E501
from . import BaseTestCase


class TestSectionController(BaseTestCase):
    """SectionController integration test stubs"""

    def test_section_delete(self):
        """Test case for section_delete

        Delete a section
        """
        query_string = [('section_id', 56)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/section',
            method='DELETE',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_section_get(self):
        """Test case for section_get

        Get list of sections or selected section
        """
        query_string = [('section_name', 'section_name_example'),
                        ('page_id', 56)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/section',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_section_post(self):
        """Test case for section_post

        Create a new section
        """
        section_request = {"page_id":1,"section_name":"Hero Banner","fields":"{}"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/section',
            method='POST',
            headers=headers,
            data=json.dumps(section_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_section_put(self):
        """Test case for section_put

        Update an existing section
        """
        section_request = {"page_id":1,"section_name":"Hero Banner","fields":"{}"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/section',
            method='PUT',
            headers=headers,
            data=json.dumps(section_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
