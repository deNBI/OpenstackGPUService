# coding: utf-8

from __future__ import absolute_import

import json
import unittest.mock

import openapi_server.controllers
import openapi_server.denbi
import openapi_server.test


@unittest.mock.patch('openapi_server.denbi.create_osclient')
class TestDefaultController(openapi_server.test.FlaskTestCase):
    """DefaultController integration test stubs"""

    def setUp(self) -> None:
        # disable memcached
        openapi_server.controllers.enable_memcache(False)

    def test_gpus_flavors_flavor_openstack_id_get(self, mock) -> None:
        """Test case for gpus_flavors_flavor_openstack_id_get
           Get specific GPU-Flavor with Info of available and total GPU count
        """
        openapi_server.test.mock_openstack_connection(mock)
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Basic Zm9vOmJhcg==',
        }
        # ask for flavor with id 'a54ed137-04fe-463f-a2b0-666079d1b2ba'
        response = self.client.open(
            '/gpus/flavors/{flavor_openstack_id}'.format(flavor_openstack_id='a54ed137-04fe-463f-a2b0-666079d1b2ba'),
            method='GET',
            headers=headers)
        # should result in a 200 status code
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # validate response
        result = json.loads(response.data.decode('utf-8'))
        self.assertEqual(4, result["flavor"]["total"])
        self.assertEqual(3, result["flavor"]["available"])

        # ask for an unknown flavor id
        response = self.client.open(
            '/gpus/flavors/{flavor_openstack_id}'.format(flavor_openstack_id='gibt_es_nicht'),
            method='GET',
            headers=headers)
        # should result in a 404 status code
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_gpus_flavors_get(self, mock):
        """Test case for gpus_flavors_get

        List all GPU-Flavors with count.
        """
        openapi_server.test.mock_openstack_connection(mock)
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

        # validate response @see
        for flavor in (json.loads(response.data.decode('utf-8')))["flavors"]:
            if flavor["flavor_name"] == "de.NBI GPU V100 medium":
                self.assertEqual(flavor["total"], 4)
                self.assertEqual(flavor["available"], 3)
            elif flavor["flavor_name"] == "de.NBI GPU V100 large":
                self.assertEqual(flavor["total"], 4)
                self.assertEqual(flavor["available"], 3)
            elif flavor["flavor_name"] == "de.NBI 2 GPU V100 large":
                self.assertEqual(flavor["total"], 2)
                self.assertEqual(flavor["available"], 1)
            else:
                self.fail(f"Unkown flavor '{flavor['name']}'.")


if __name__ == '__main__':
    unittest.main()
