import logging

from flask import Blueprint, jsonify, Response

from ..auth.FlaskAuth0 import get_remote_ip

LOGGER = logging.getLogger(__name__)

def create_control_blueprint(reload_fn):
  blueprint = Blueprint('control', __name__)

  @blueprint.route("/reload", methods=['POST'])
  def _control_reload() -> Response:
    remote_ip = get_remote_ip()
    if remote_ip != '127.0.0.1':
      return jsonify({'ip': remote_ip}), 403
    LOGGER.info("reloading...")
    reload_fn()
    return jsonify({'status': 'OK'})

  return blueprint
