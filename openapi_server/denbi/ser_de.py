""" Serializer - Deserializer module."""
import json


class JsonSerDe:
    """ Implements a (en-)coding safe (de-)serializer for Json objects.
        Implementation can be used as ser[ialize]de[serialize]er for
        pymemcache client.
        See https://pymemcache.readthedocs.io/en/latest/getting_started.html#serialization
    """

    def serialize(self, key, value): # pylint: disable=W0613
        """ Serialize value."""
        if isinstance(value, str):
            return value.encode('utf-8'), 1
        return json.dumps(value).encode('utf-8'), 2

    def deserialize(self, key, value, flags): # pylint: disable=W0613
        """ Deserialize value."""
        if flags == 1:
            return value.decode('utf-8')
        if flags == 2:
            return json.loads(value.decode('utf-8'))
        raise Exception("Unknown serialization format")
