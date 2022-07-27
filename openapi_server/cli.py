import argparse
import datetime
import json

from pymemcache.client.base import Client as MemCachedClient

from openapi_server.denbi.Resources import GPUResources as Resources
from openapi_server.denbi.SerDe import JsonSerDe as SerDe
from openapi_server.encoder import JSONEncoder

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Create a list of available flavors.")
    parser.add_argument("--memcached", help="Use memcached server",
                        action="store_true",
                        default=False)
    parser.add_argument("--memcachedHost",
                        help="Combination of host:port where a memcached server listened.",
                        type=str,
                        default="127.0.0.1:11211")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--flavorId",
                       help="Ask for availability of specific flavor id. ",
                       type=str)
    group.add_argument("--flavorName",
                       help="Ask for availability of specific flavor name. ",
                       type=str)

    args = parser.parse_args()

    resources = Resources()
    flavors = []

    if args.memcached:
        memcachedclient = MemCachedClient(args.memcachedHost, serde=SerDe())
        # check if memcached contains a list of flavors
        flavors = memcachedclient.get('FlavorGPU')
        if memcachedclient.get('FlavorGPU.timestamp'):
            timestamp = datetime.datetime.strptime(memcachedclient.get('FlavorGPU.timestamp'), '%Y-%m-%d %H:%M:%S')
        else:
            flavors = None

    if not flavors:
        resources.update()
        flavors = json.loads(json.dumps(resources.gpu_flavors(), cls=JSONEncoder))
        if args.memcached:
            timestamp = datetime.datetime.now()
            memcachedclient.set("FlavorGPU", flavors)
            memcachedclient.set("FlavorGPU.timestamp", timestamp.strftime('%Y-%m-%d %H:%M:%S'))

    if args.flavorId or args.flavorName:
        foundFlavor = None
        for flavor in flavors:
            if flavor['flavor_openstack_id'] == args.flavorId or flavor['flavor_name'] == args.flavorName:
                foundFlavor = flavor
                break

        if foundFlavor:
            print(json.dumps(flavor, cls=JSONEncoder, sort_keys=True, indent=4));
        else:
            if (args.flavorId):
                print("Unknown flavor id!")
            else:
                print("Unknown flavor name!")

    else:
        print(json.dumps(flavors, cls=JSONEncoder, sort_keys=True, indent=4))
