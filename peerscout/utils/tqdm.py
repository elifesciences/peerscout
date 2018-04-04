from functools import wraps
import os
import sys

from tqdm import tqdm as _tqdm

MIN_INTERVAL_KEY = 'TQDM_MIN_INTERVAL'

DEFAULT_NON_ATTY_MIN_INTERVAL = 10.0

def _is_real_terminal_output():
  return sys.stderr.isatty()

@wraps(_tqdm)
def tqdm(*args, **kwargs):
  min_interval = os.environ.get(MIN_INTERVAL_KEY)

  if not min_interval and not _is_real_terminal_output():
    min_interval = DEFAULT_NON_ATTY_MIN_INTERVAL

  if min_interval:
    kwargs = {
      **kwargs,
      'mininterval': float(min_interval)
    }

  return _tqdm(*args, **kwargs)
