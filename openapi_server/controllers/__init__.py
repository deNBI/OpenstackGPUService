import json
from datetime import datetime

from pymemcache.client.base import Client as MemCachedClient

import openapi_server.denbi.Resources
from openapi_server.denbi.SerDe import JsonSerDe as SerDe
from openapi_server.encoder import JSONEncoder

memcache = True
memcachedHost = "127.0.0.1:11211"
memcachedClient = MemCachedClient(memcachedHost, serde=SerDe())


def enable_memcache(enabled):
    global memcache
    memcache = enabled


def configure_memcache(enabled=True, host="127.0.0.1:11211"):
    global memcache, memcachedHost, memcachedClient
    memcache = enabled
    memcachedHost = host
    memcachedClient = MemCachedClient(memcachedHost, serde=SerDe())


def getFlavors():
    flavors = []
    if memcache:
        # check if memcached contains a list of flavors
        flavors = memcachedClient.get('FlavorGPU')
        if memcachedClient.get('FlavorGPU.timestamp'):
            timestamp = datetime.strptime(memcachedClient.get('FlavorGPU.timestamp'), '%Y-%m-%d %H:%M:%S')

    if not flavors:
        resources = openapi_server.denbi.Resources.GPUResources()
        resources.update()
        flavors = json.loads(json.dumps(resources.gpu_flavors(), cls=JSONEncoder))
        timestamp = datetime.now()
        if memcache:
            # update memcached
            memcachedClient.set("FlavorGPU", flavors)
            memcachedClient.set("FlavorGPU.timestamp", timestamp.strftime('%Y-%m-%d %H:%M:%S'))

    return {"flavors": flavors, "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S')}


def getFlavorbyId(flavorId):
    flavors = getFlavors()
    for flavor in flavors["flavors"]:
        if flavor['flavor_openstack_id'] == flavorId:
            return {"flavor": flavor, "timestamp": flavors["timestamp"]}
            break

    return None
