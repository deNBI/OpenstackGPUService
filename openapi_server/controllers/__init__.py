""" Controller module providing some general functions """
import json
from datetime import datetime

from pymemcache.client.base import Client as MemCachedClient

import openapi_server.denbi.resources
from openapi_server.denbi.ser_de import JsonSerDe as SerDe
from openapi_server.encoder import JSONEncoder

MEMCACHE = True
MEMCACHEDHOST = "127.0.0.1:11211"
MEMCACHEEXPIREAFTER = 300
MEMCACHEDCLIENT = MemCachedClient(MEMCACHEDHOST, serde=SerDe())

def __get_flavors_as_json_():
    """
    Internal functions. Create a new GPUResource obj, updates data, and returns list of
    available flavor in json format

    :return: list of flavors in json format
    """
    resources = openapi_server.denbi.resources.GPUResources()
    resources.update()
    return json.loads(json.dumps(resources.gpu_flavors(), cls=JSONEncoder))


def enable_memcache(enabled=True):
    """
    Enable (or disable) memcached support
    :param enabled: Enabled memcached support, defaults to True
    :return: None
    """
    global MEMCACHE # pylint: disable=W0603
    MEMCACHE = enabled


def configure_memcache(enabled=True, host="127.0.0.1:11211", expire=300, prefix=""):
    """
    Configure memcache.
    :param enabled: Enabled memcached support, defaults to True
    :param host: memcached host as string "<ip>:<port>", defaults to "127.0.0.1:11211"
    :param expire : time in seconds after cache expires, default to 300
    :param prefix : optional memcached key prefix, default to ""
    :return: None
    """
    global MEMCACHE, MEMCACHEDHOST, MEMCACHEDCLIENT, MEMCACHEEXPIREAFTER, MEMCACHEDPREFIX # pylint: disable=W0603
    MEMCACHE = enabled
    MEMCACHEDHOST = host
    MEMCACHEEXPIREAFTER = expire
    MEMCACHEDCLIENT = MemCachedClient(MEMCACHEDHOST, serde=SerDe())
    MEMCACHEDPREFIX = prefix


def get_flavors():
    """
    Return a dict containing a list of GPU flavors together with a timestamp.

    If MemCached is enabled, asked the configured MemCached Server for cached data.


    :return:
    """
    flavors = []
    timestamp = datetime.now()
    if MEMCACHE:
        # check if memcached contains a list of flavors
        flavors = MEMCACHEDCLIENT.get(MEMCACHEDPREFIX+'FlavorGPU')
        if MEMCACHEDCLIENT.get(MEMCACHEDPREFIX+'FlavorGPU.timestamp'):
            timestamp = datetime.strptime(MEMCACHEDCLIENT.get(MEMCACHEDPREFIX+'FlavorGPU.timestamp'), '%Y-%m-%d %H:%M:%S')

    if not flavors:
        flavors = __get_flavors_as_json_()
        if MEMCACHE:
            # update memcached
            MEMCACHEDCLIENT.set(MEMCACHEDPREFIX+"FlavorGPU", flavors, MEMCACHEEXPIREAFTER)
            MEMCACHEDCLIENT.set(MEMCACHEDPREFIX+"FlavorGPU.timestamp", timestamp.strftime('%Y-%m-%d %H:%M:%S'), MEMCACHEEXPIREAFTER)

    return {"flavors": flavors, "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S')}


def get_flavor_by_id(flavorid):
    """
    Return a flavor specified by given flavor_id or None if id is not found.

    :param flavorid: id of searched flavor.
    :return: Return searched flavor or None.
    """
    flavors = get_flavors()
    for flavor in flavors["flavors"]:
        if flavor['flavor_openstack_id'] == flavorid:
            return {"flavor": flavor, "timestamp": flavors["timestamp"]}

    return None


def update_cache():
    """
    Updates the cached data stored in the configured MemCached service.
    :return: None
    """
    MEMCACHEDCLIENT.set(MEMCACHEDPREFIX+"FlavorGPU", __get_flavors_as_json_(), MEMCACHEEXPIREAFTER)
    MEMCACHEDCLIENT.set(MEMCACHEDPREFIX+"FlavorGPU.timestamp", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), MEMCACHEEXPIREAFTER)
