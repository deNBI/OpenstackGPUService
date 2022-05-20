from datetime import datetime
from pymemcache.client.base import Client as MemCachedClient
from openapi_server.denbi.SerDe import JsonSerDe as SerDe
from openapi_server.denbi.Resources import GPUResources as Resources

import json
from openapi_server.encoder import JSONEncoder

memcachedHost = "127.0.0.1:11211"
memcachedclient = MemCachedClient(memcachedHost,serde=SerDe())
resources = Resources()


def getFlavors():
    flavors = []
     # check if memcached contains a list of flavors
    flavors = memcachedclient.get('FlavorGPU')
    if memcachedclient.get('FlavorGPU.timestamp') :
        timestamp = datetime.strptime(memcachedclient.get('FlavorGPU.timestamp'),'%Y-%m-%d %H:%M:%S')
    else:
        flavors = None

    if not flavors:
        resources.update()
        flavors = json.loads(json.dumps(resources.gpu_flavors(), cls=JSONEncoder))
        # update memcached
        timestamp = datetime.datetime.now()
        memcachedclient.set("FlavorGPU",flavors)
        memcachedclient.set("FlavorGPU.timestamp",timestamp.strftime('%Y-%m-%d %H:%M:%S'))

    return { "flavors":flavors, "timestamp":timestamp }

def getFlavorbyId(flavorId):
    flavors = getFlavors()
    for flavor in flavors["flavors"]:
        if flavor['flavor_openstack_id'] == flavorId:
            return { "flavor": flavor, "timestamp":flavors["timestamp"]}
            break

    return None