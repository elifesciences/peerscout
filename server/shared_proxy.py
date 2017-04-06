import sys
from os.path import dirname, abspath
from importlib import import_module

root = dirname(dirname(abspath(__file__)))
sys.path.insert(1, root)

# this is a bit hacky, python doesn't like main scripts in a sub directory / package
pkg = import_module('shared')
for k, v in list(pkg.__dict__.items()):
  globals()[k] = v
