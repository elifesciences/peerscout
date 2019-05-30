from functools import wraps, partial
import os
import sys

from tqdm import tqdm as _tqdm

MIN_INTERVAL_KEY = 'TQDM_MIN_INTERVAL'

DEFAULT_NON_ATTY_MIN_INTERVAL = 10.0

TQDM_DESCRIPTION_FUNCTIONS = [
    'set_description',
    'set_description_str',
    'set_postfix',
    'set_postfix_str'
]


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

    tqdm_instance = _tqdm(*args, **kwargs)

    if min_interval:
        for f_name in TQDM_DESCRIPTION_FUNCTIONS:
            setattr(
                tqdm_instance,
                f_name,
                partial(getattr(tqdm_instance, f_name), refresh=False)
            )

    return tqdm_instance


tqdm.pandas = wraps(_tqdm.pandas)(lambda: _tqdm.pandas())  # pylint: disable=unnecessary-lambda
