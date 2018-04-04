import logging
import os

from flask import Blueprint

from peerscout.utils.flask import no_cache

LOGGER = logging.getLogger(__name__)

def get_client_folder():
  return os.path.abspath('client/dist')

def create_client_blueprint():
  client_folder = get_client_folder()
  LOGGER.debug('client dir: %s', client_folder)

  blueprint = Blueprint('client', __name__, static_folder=client_folder, static_url_path='')

  @blueprint.route('/')
  @no_cache
  def _send_index():
    return blueprint.send_static_file('index.html')

  return blueprint
