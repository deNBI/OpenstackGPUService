import connexion

from openapi_server import encoder


def app():
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'OpenStack GPU Service'},
                pythonic_params=True)
    return app