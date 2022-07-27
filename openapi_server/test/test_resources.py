"""
Tests for GPUResources.
"""

import unittest
from unittest.mock import patch

import openapi_server.denbi
import openapi_server.test
from openapi_server.denbi.resources import GPUResources, GPUResourceException


@patch('openapi_server.denbi.create_osclient')
class TestGPUResources(unittest.TestCase):
    """GPUResources integration tests."""

    def test_update(self, mock):
        '''
        Test GPUResources.update() function mocking openstack API functions.

        :param mock: mocked create osclient function
        :return:
        '''

        openapi_server.test.mock_openstack_connection(mock)

        # create new GPUResource object
        res = GPUResources()
        # and update data
        res.update()

        # test data contains 3 hypervisor at all
        self.assertEqual(3, len(res.__hypervisors__))
        # test data contains 2 aggregate at all, but only one gpu aggregate
        self.assertEqual(1, len(res.__gpu_aggregates__))
        # test data contains 6 gpu flavors at all, but only 3 gpu flavors
        self.assertEqual(3, len(res.__gpu_flavors__))

        self.assertEqual(1, len(res.__gpu_instances_by_host__.keys()))

    def test_gpu_flavors(self, mock):
        openapi_server.test.mock_openstack_connection(mock)

        res = GPUResources()
        res.update()

        flavors = res.gpu_flavors()
        # 3 different flavors are expected :
        # - de.NBI GPU V100 medium (4 total, 3 available)
        # - de.NBI GPU V100 large (4 total, 3 available)
        # - de.NBI 2 GPU V100 large (2 total, 1 available)
        self.assertEqual(3, len(flavors))
        for flavor in flavors:
            if flavor.flavor_name == "de.NBI GPU V100 medium":
                self.assertEqual(4, flavor.total, "Expected 4 flavor of type 'de.NBI GPU V100 medium' in total.")
                self.assertEqual(3, flavor.available, "Expected 3 flavor of type 'de.NBI GPU V100 medium' available.")
            elif flavor.flavor_name == "de.NBI GPU V100 large":
                self.assertEqual(4, flavor.total, "Expected 4 flavor of type 'de.NBI GPU V100 large' in total.")
                self.assertEqual(3, flavor.available, "Expected 3 flavor of type 'de.NBI GPU V100 large' available.")
            elif flavor.flavor_name == "de.NBI 2 GPU V100 large":
                self.assertEqual(2, flavor.total, "Expected 2 flavor of type 'de.NBI 2 GPU V100 large' in total.")
                self.assertEqual(1, flavor.available, "Expected 1 flavor of type 'de.NBI 2 GPU V100 large' available.")
            else:
                self.fail("Unexpected flavor.")

    def test_gpu_flavor(self, mock):
        openapi_server.test.mock_openstack_connection(mock)

        res = GPUResources()
        res.update()

        #  ask for de.NBI GPU V100 medium flavors
        try:
            flavor = res.gpu_flavor("a54ed137-04fe-463f-a2b0-666079d1b2ba")
        except GPUResourceException:
            self.fail("Expected flavor ('a54ed137-04fe-463f-a2b0-666079d1b2ba') not found.")

        self.assertEqual(4, flavor.total, "Expected 4 flavor of type 'de.NBI GPU V100 medium' in total.")
        self.assertEqual(3, flavor.available, "Expected 3 flavor of type 'de.NBI GPU V100 medium' available.")

        #  ask for de.NBI GPU V100 large flavors
        try:
            flavor = res.gpu_flavor("4e6428f5-a0ec-4450-8f38-112236f056da")
        except GPUResourceException:
            self.fail("Expected flavor ('4e6428f5-a0ec-4450-8f38-112236f056da') not found.")

        self.assertEqual(4, flavor.total, "Expected 4 flavor of type 'de.NBI GPU V100 large' in total.")
        self.assertEqual(3, flavor.available, "Expected 3 flavor of type 'de.NBI GPU V100 large' available.")

        #  ask for de.NBI 2 GPU V100 large flavors
        try:
            flavor = res.gpu_flavor("9a8a5bfc-001e-469b-a787-ddbbc2ea8483")
        except GPUResourceException:
            self.fail("Expected flavor ('9a8a5bfc-001e-469b-a787-ddbbc2ea8483') not found.")

        self.assertEqual(2, flavor.total, "Expected 2 flavor of type 'de.NBI 2 GPU V100 large' in total.")
        self.assertEqual(1, flavor.available, "Expected 1 flavor of type 'de.NBI 2 GPU V100 large' available.")

        # ask for an unknown flavor -> should fail
        try:
            flavor = res.gpu_flavor("gibt_es_nicht")
            self.fail("A flavor with id 'gibt_es_nicht' isn't present in mocked test data.")
        except GPUResourceException:
            pass


if __name__ == '__main__':
    unittest.main()
