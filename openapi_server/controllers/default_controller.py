import connexion
import six

from openapi_server.models.flavor_gpu import FlavorGPU  # noqa: E501
from openapi_server.models.model404 import Model404  # noqa: E501
from openapi_server import util


def gpus_flavors_flavor_openstack_id_get(flavor_openstack_id):  # noqa: E501
    """Get specific GPU-Flavor with Info of available and total GPU count

     # noqa: E501

    :param flavor_openstack_id: 
    :type flavor_openstack_id: str

    :rtype: FlavorGPU
    """
    return 'do some magic!'


def gpus_flavors_get():  # noqa: E501
    """List all GPU-Flavors with count

     # noqa: E501


    :rtype: List[FlavorGPU]
    """
    return 'do some magic!'
