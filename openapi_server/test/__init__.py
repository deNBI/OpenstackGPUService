""" Tests """
import json
import logging
from pathlib import Path
from unittest.mock import MagicMock

import connexion
import flask_testing

from openapi_server.encoder import JSONEncoder


def mock_openstack_connection(mock):
    mock_osclient = MagicMock()
    with open(Path(__file__).parent / "list_aggregates.json", encoding='utf-8') as file_handler:
        mock_osclient.list_aggregates.return_value = json.load(file_handler)
        file_handler.close()

    with open(Path(__file__).parent / "list_servers.json", encoding='utf-8') as file_handler:
        mock_osclient.list_servers.return_value = json.load(file_handler)
        file_handler.close()

    with open(Path(__file__).parent / "list_hypervisors.json", encoding='utf-8') as file_handler:
        mock_osclient.list_hypervisors.return_value = json.load(file_handler)
        file_handler.close()

    with open(Path(__file__).parent / "list_flavors.json", encoding='utf-8') as file_handler:
        mock_osclient.list_flavors.return_value = json.load(file_handler)
        file_handler.close()

    mock.return_value = mock_osclient


class FlaskTestCase(flask_testing.TestCase):
    """ Subclass of flask_testing.TestCase, overwriting create_app. """

    def create_app(self):
        logging.getLogger('connexion.operation').setLevel('ERROR')
        app = connexion.App(__name__, specification_dir='../openapi/')
        app.app.json_encoder = JSONEncoder
        app.add_api('openapi.yaml', pythonic_params=True)
        return app.app
