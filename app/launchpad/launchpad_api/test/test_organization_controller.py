import unittest

from flask import json

from models.organization_request import OrganizationRequest  # noqa: E501
from . import BaseTestCase


class TestOrganizationController(BaseTestCase):
    """OrganizationController integration test stubs"""

    def test_organization_delete(self):
        """Test case for organization_delete

        Delete an organization
        """
        query_string = [('organization_id', 56)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/organization',
            method='DELETE',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_organization_get(self):
        """Test case for organization_get

        Get list of organizations
        """
        query_string = [('organization_id', 56)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/organization',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_organization_post(self):
        """Test case for organization_post

        Create a new organization
        """
        organization_request = {"name":"Acme Corporation","description":"Leading provider of industrial automation solutions.","unit_code":"ACME001","id":0,"organization_logo":"https://example.com/uploads/acme_logo.png","sector":"Manufacturing"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/organization',
            method='POST',
            headers=headers,
            data=json.dumps(organization_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_organization_put(self):
        """Test case for organization_put

        Update an existing organization
        """
        organization_request = {"name":"Acme Corporation","description":"Leading provider of industrial automation solutions.","unit_code":"ACME001","id":0,"organization_logo":"https://example.com/uploads/acme_logo.png","sector":"Manufacturing"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/organization',
            method='PUT',
            headers=headers,
            data=json.dumps(organization_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
