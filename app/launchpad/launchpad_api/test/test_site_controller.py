import unittest

from flask import json

from launchpad_api.models.site_request import SiteRequest  # noqa: E501
from launchpad_api.test import BaseTestCase


class TestSiteController(BaseTestCase):
    """SiteController integration test stubs"""

    def test_site_delete(self):
        """Test case for site_delete

        Delete a site
        """
        query_string = [('site_id', 'site_id_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/site',
            method='DELETE',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_site_get(self):
        """Test case for site_get

        Get list of sites
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/site',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_site_post(self):
        """Test case for site_post

        Create a new site
        """
        site_request = {"name":"Main Website","id":0,"status":"status"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/site',
            method='POST',
            headers=headers,
            data=json.dumps(site_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_site_put(self):
        """Test case for site_put

        Update an existing site
        """
        site_request = {"name":"Main Website","id":0,"status":"status"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/site',
            method='PUT',
            headers=headers,
            data=json.dumps(site_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
