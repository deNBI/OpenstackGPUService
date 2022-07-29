""" Commandline Server """ # pylint: disable=invalid-name
import argparse
import datetime
import os
import time
import logging

import gunicorn.app.base
import openapi_server
import openapi_server.controllers

# create simple Logger to updateCache messages to console
LOG = logging.getLogger('updateCache')
HANDLER = logging.StreamHandler()
HANDLER.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s", datefmt='%Y-%d-%m %I:%M:%S %z')
HANDLER.setFormatter(formatter)
LOG.addHandler(HANDLER)
LOG.setLevel(logging.DEBUG)

class StandaloneApplication(gunicorn.app.base.BaseApplication):
    """
      Customized unicorn application to run gunicorn inside a Python
      application.

      see https://docs.gunicorn.org/en/stable/custom.html
    """

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        """ overwrite gunicorn.app.base.BaseApplication.load_config() """
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        """ overwrite gunicorn.app.base.BaseApplication.load() """
        return self.application


def update_cache():
    """ Helper function. Updates cached data continuously. """
    LOG.info("Start updating cached data continuously.")
    while True:
        start = datetime.datetime.now()
        openapi_server.controllers.update_cache()
        stop = datetime.datetime.now()
        runningtime = (stop-start).seconds
        LOG.info("Updating cached data took %d seconds.", runningtime)
        sleepingtime = max(0, int(openapi_server.controllers.MEMCACHEEXPIREAFTER/2)-runningtime)
        LOG.info("Sleeping for %d seconds.", sleepingtime)
        time.sleep(sleepingtime)

if __name__ == '__main__':

    PARSER = argparse.ArgumentParser("Run a OpenstackGPUServer.")
    PARSER.add_argument("--memcachedHost",
                        help="Combination of host:port where a memcached server listened.",
                        type=str,
                        default="127.0.0.1:11211")
    PARSER.add_argument("--bind",
                        help="Update cache only, implies option --memcached and forces updating the cache.",
                        type=str,
                        default="127.0.0.1:8080")
    PARSER.add_argument("--workers",
                        help="Workers started b",
                        type=int,
                        default=4)

    ARGS = PARSER.parse_args()

    # validate arguments
    MEMCACHEDHOST = ARGS.memcachedHost.split(":")
    BIND = ARGS.bind.split(":")
    WORKERS = ARGS.workers

    # configure memcached
    openapi_server.controllers.configure_memcache(enabled=True,
                                                  host=MEMCACHEDHOST,
                                                  expire=300)

    # run gunicorn in a separate child process
    if os.fork() == 0:
        # child
        OPTIONS = {
            'bind': f"{BIND[0]}:{BIND[1]}",
            'workers': WORKERS
        }
        StandaloneApplication(openapi_server.app(), OPTIONS).run()
    else:
        # parent
        update_cache()
