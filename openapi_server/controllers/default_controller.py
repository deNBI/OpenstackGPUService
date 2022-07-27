"""
Auto generated by OpenAPI Generator (https://openapi-generator.tech).
"""
import openapi_server.controllers as controller
from openapi_server.models.model404 import Model404  # noqa: E501


def gpus_flavors_flavor_openstack_id_get(flavor_openstack_id):  # noqa: E501
    """Get specific GPU-Flavor with Info of available and total GPU count

     # noqa: E501

    :param flavor_openstack_id:
    :type flavor_openstack_id: str

    :rtype: object
    """
    flavor = controller.getFlavorbyId(flavor_openstack_id)

    if not flavor:
        return Model404("Unkown flavor id!"), 404

    return controller.getFlavorbyId(flavor_openstack_id)


def gpus_flavors_get():  # noqa: E501
    """List all GPU-Flavors with count

     # noqa: E501


    :rtype: object
    """
    return controller.getFlavors()
