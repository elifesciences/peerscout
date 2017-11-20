import logging

from importlib import import_module

NAME = 'updateDataAndReload'

def main():
  logger = logging.getLogger(NAME)
  try:
    scripts = [
      'importDataToDatabase',
      'convertEditorsCsv',
      'importEarlyCareerResearchersCsv',
      'enrichEarlyCareerResearchersInDatabase',
      'generateTextTokens',
      'generateLdaDocVec',
      'generateDoc2Vec',
      'reloadServer'
    ]
    if not import_module('downloadFiles').main():
      logger.info("no files downloaded, skipping further processing")
      return False
    for script in scripts:
      logger.info("running: %s", script)
      pkg = import_module(script)
      pkg.main()
    logger.info("done")
    return True
  except Exception as e:
    logger.exception(e)
    raise e

if __name__ == "__main__":
  from shared_proxy import configure_logging
  configure_logging('update')

  main()
