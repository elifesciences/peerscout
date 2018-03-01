import os
import datetime
import logging

from flask import Flask
from flask.json import JSONEncoder
from flask_cors import CORS

from ..shared.app_config import get_app_config
from ..shared.logging_config import configure_logging

from .blueprints.api import create_api_blueprint
from .blueprints.control import create_control_blueprint
from .blueprints.client import create_client_blueprint

LOGGER = logging.getLogger(__name__)

class CustomJSONEncoder(JSONEncoder):
  def default(self, obj): # pylint: disable=E0202
    try:
      if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        return obj.isoformat()
    except TypeError:
      pass
    return JSONEncoder.default(self, obj)

def create_app(config):
  app = Flask(__name__)
  app.json_encoder = CustomJSONEncoder
  CORS(app)

  api, reload_api = create_api_blueprint(config)
  app.register_blueprint(api, url_prefix='/api')

  control = create_control_blueprint(
    reload_fn=reload_api
  )
  app.register_blueprint(control, url_prefix='/control')

  app.register_blueprint(create_client_blueprint())

  return app

def initialize_logging():
  configure_logging('server')
  logging.getLogger('summa.preprocessing.cleaner').setLevel(logging.WARNING)

def main():
  config = get_app_config()
  port = config.get('server', 'port', fallback=8080)
  host = config.get('server', 'host', fallback=None)
  app = create_app(config)
  app.run(port=port, host=host, threaded=True)

if __name__ == "__main__":
  main()
