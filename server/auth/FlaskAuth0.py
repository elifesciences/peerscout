from flask import request

from .Auth0 import Auth0

def get_access_token():
  return request.headers.get('X-Access-Token')

def get_remote_ip():
  x_forwarded_for = request.headers.getlist('X-Forwarded-For')
  if x_forwarded_for and len(x_forwarded_for) > 0:
    print(x_forwarded_for)
    return x_forwarded_for[0]
  return request.remote_addr

def requires_auth(allowed_ips):
  return get_remote_ip() not in allowed_ips

def not_authorized_request_handler():
  return ('Not Authorized', 401)

def parse_allowed_ips(allowed_ips):
  allowed_ips = allowed_ips.strip() if allowed_ips else ''
  if not allowed_ips:
    return set()
  return {s.strip().lower() for s in allowed_ips.split(',')} - {''}

class FlaskAuth0(object):
  def __init__(self, allowed_ips, **kwargs):
    self.requires_auth = lambda: requires_auth(allowed_ips)
    self.auth0 = Auth0(
      **kwargs
    )

  def wrap_request_handler(self, f):
    return self.auth0.wrap_request_handler(
      f,
      get_access_token,
      not_authorized_request_handler,
      requires_auth=self.requires_auth
    )
