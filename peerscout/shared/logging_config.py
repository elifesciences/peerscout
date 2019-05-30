import logging
from logging.handlers import TimedRotatingFileHandler
import os


def configure_logging(name):
    logging.getLogger().setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(console_handler)

    log_filename = os.path.abspath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../../logs/%s.log' % name
    ))
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    file_handler = TimedRotatingFileHandler(
        filename=log_filename,
        when='midnight',
        backupCount=int(os.environ.get('PEERSCOUT_MAX_LOG_DAYS', 842))
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logging.getLogger().addHandler(file_handler)
