import json
import logging

import requests

def get_logger():
  return logging.getLogger(__name__)

class Auth0(object):
  def __init__(self, domain, is_valid_email=None):
    self.domain = domain
    self.is_valid_email = is_valid_email or (lambda _: True)

  def get_user_info(self, access_code):
    response = requests.get('https://{}/userinfo/?access_token={}'.format(self.domain, access_code))
    response.raise_for_status()
    return json.loads(response.text)

  def verify_access_token_and_get_email(self, access_token):
    try:
      user_info = self.get_user_info(access_token)
      email = user_info.get('email')
      get_logger().info('email: %s', email)
      return email
    except Exception as e:
      get_logger().debug('access token not valid: %s', e)
      return None

  def wrap_request_handler(
    self, request_handler, get_access_token, not_authorized_handler, requires_auth=None):

    def wrapped_request_handler():
      if requires_auth is not None and not requires_auth():
        return request_handler()
      access_token = get_access_token()
      if not access_token:
        get_logger().info('no access token provided')
      email = self.verify_access_token_and_get_email(access_token) if access_token else None
      if email and self.is_valid_email(email):
        return request_handler(email=email)
      else:
        get_logger().info('invalid email: %s', email)
        return not_authorized_handler()
    return wrapped_request_handler
