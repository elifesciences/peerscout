import csv
import logging
from io import StringIO

LOGGER = logging.getLogger(__name__)

DEFAULT_CSV_FILE_HEADER = 'Query: Xyz\nGenerated on ...\n\n'


def create_csv_content(data, fieldnames, header=DEFAULT_CSV_FILE_HEADER):
    LOGGER.debug('data: %s', data)
    out = StringIO()
    out.write(header)
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    return out.getvalue()
