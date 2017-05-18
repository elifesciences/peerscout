import configparser
import os

def get_app_config_filename():
  return os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../app.cfg'
  )

def read_app_config():
  config = configparser.ConfigParser()
  config.read(get_app_config_filename())
  return config

class simple_memoize(object):
  def __init__(self, fn):
    self.fn = fn
    self.cache = None

  def __call__(self):
    if self.cache is None:
      self.cache = self.fn()
    return self.cache


get_app_config = simple_memoize(read_app_config)
