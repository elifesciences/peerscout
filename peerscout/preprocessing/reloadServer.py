import logging

import requests

NAME = 'reloadServer'

def main():
  logger = logging.getLogger(NAME)
  try:
    response = requests.post('http://localhost:8080/control/reload')
    response.raise_for_status()
    logger.debug("response: %s", response.text)
  except requests.exceptions.ConnectionError:
    logger.warning("server doesn't seem to be running")
  logger.info("done")

if __name__ == "__main__":
  from ..shared.logging_config import configure_logging
  configure_logging('update')

  main()
