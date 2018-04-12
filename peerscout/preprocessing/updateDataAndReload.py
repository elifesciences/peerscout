import logging

from importlib import import_module

from . import downloadFiles

LOGGER = logging.getLogger(__name__)

NAME = 'updateDataAndReload'

_MODULE_PREFIX = __package__ + '.'

MODULE_NAMES = [
  _MODULE_PREFIX + name
  for name in [
    'importDataToDatabase',
    'convertEditorsCsv',
    'import_editor_roles_and_keywords_csv',
    'importEarlyCareerResearchersCsv',
    'enrichData',
    'generateTextTokens',
    'generateLdaDocVec',
    'generateDoc2Vec',
    'reloadServer'
  ]
]

def load_modules(module_names):
  for module_name in module_names:
    LOGGER.debug("loading: %s", module_name)
    pkg = import_module(module_name)
    yield pkg

def main():
  logger = logging.getLogger(NAME)
  try:
    if not downloadFiles.main():
      logger.info("no files downloaded, skipping further processing")
      return False
    modules = load_modules(MODULE_NAMES)
    for pkg in modules:
      logger.info("running: %s", pkg.__name__)
      pkg.main()
    logger.info("done")
    return True
  except Exception as e:
    logger.exception(e)
    raise e

if __name__ == "__main__":
  from peerscout.shared.logging_config import configure_logging
  configure_logging('update')

  main()
