# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.flavor_gpu import FlavorGPU  # noqa: E501
from openapi_server.models.model404 import Model404  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_gpus_flavors_flavor_openstack_id_get(self):
        """Test case for gpus_flavors_flavor_openstack_id_get

        Get specific GPU-Flavor with Info of available and total GPU count
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Basic Zm9vOmJhcg==',
        }
        response = self.client.open(
            '/gpus/flavors/{flavor_openstack_id}'.format(flavor_openstack_id='flavor_openstack_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_gpus_flavors_get(self):
        """Test case for gpus_flavors_get

        List all GPU-Flavors with count
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Basic Zm9vOmJhcg==',
        }
        response = self.client.open(
            '/gpus/flavors',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
