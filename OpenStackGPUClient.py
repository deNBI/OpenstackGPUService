""" Commandline client """ # pylint: disable=invalid-name
import argparse
import datetime
import json

from pymemcache.client.base import Client as MemCachedClient

from openapi_server.denbi.resources import GPUResources as Resources
from openapi_server.denbi.ser_de import JsonSerDe as SerDe
from openapi_server.encoder import JSONEncoder

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser("Create a list of available flavors.")
    PARSER.add_argument("--memcached", help="Use memcached server",
                        action="store_true",
                        default=False)
    PARSER.add_argument("--memcachedHost",
                        help="Combination of host:port where a memcached server listened.",
                        type=str,
                        default="127.0.0.1:11211")
    PARSER.add_argument("--update",
                        help="Update cache only, implies option --memcached and forces updating the cache.",
                        action="store_true",
                        default=False)
    PARSER.add_argument("--expire",
                        help="Time in seconds after cache values expires. Defaults to 300 seconds.",
                        type=int,
                        default=300)
    GROUP = PARSER.add_mutually_exclusive_group()
    GROUP.add_argument("--flavorId",
                       help="Ask for availability of specific flavor id. ",
                       type=str)
    GROUP.add_argument("--flavorName",
                       help="Ask for availability of specific flavor name. ",
                       type=str)

    ARGS = PARSER.parse_args()

    RESOURCES = Resources()
    FLAVORS = []

    START = datetime.datetime.now()

    if ARGS.update:
        MEMCACHEDCLIENT = MemCachedClient(ARGS.memcachedHost, serde=SerDe())

    if ARGS.memcached:
        MEMCACHEDCLIENT = MemCachedClient(ARGS.memcachedHost, serde=SerDe())
        # check if memcached contains a list of flavors
        FLAVORS = MEMCACHEDCLIENT.get('FlavorGPU')
        if MEMCACHEDCLIENT.get('FlavorGPU.timestamp'):
            TIMESTAMP = datetime.datetime.strptime(MEMCACHEDCLIENT.get('FlavorGPU.timestamp'), '%Y-%m-%d %H:%M:%S')
        else:
            FLAVORS = None

    if not FLAVORS:
        RESOURCES.update()
        FLAVORS = json.loads(json.dumps(RESOURCES.gpu_flavors(), cls=JSONEncoder))
        if ARGS.memcached or ARGS.update:
            TIMESTAMP = datetime.datetime.now()
            MEMCACHEDCLIENT.set("FlavorGPU",
                                FLAVORS,
                                expire=ARGS.expire)
            MEMCACHEDCLIENT.set("FlavorGPU.timestamp",
                                TIMESTAMP.strftime('%Y-%m-%d %H:%M:%S'),
                                expire=ARGS.expire)

    STOP = datetime.datetime.now()

    if ARGS.flavorId or ARGS.flavorName:
        FOUNDFLAVOR = None
        for flavor in FLAVORS:
            if flavor['flavor_openstack_id'] == ARGS.flavorId or flavor['flavor_name'] == ARGS.flavorName:
                FOUNDFLAVOR = flavor
                break

        if FOUNDFLAVOR:
            print(json.dumps(FOUNDFLAVOR, cls=JSONEncoder, sort_keys=True, indent=4))
        else:
            if ARGS.flavorId:
                print("Unknown flavor id!")
            else:
                print("Unknown flavor name!")

    else:
        if ARGS.update:
            print(f"Cache updated  in {(STOP-START).seconds} seconds.")
        else:
            print(json.dumps(FLAVORS, cls=JSONEncoder, sort_keys=True, indent=4))
