import os.path

from ..shared.app_config import get_app_config


def get_data_path(name=None):
    config = get_app_config()
    root_path = config.get('data', 'data_root', fallback='.data')
    if name is not None:
        return os.path.join(root_path, name)
    return root_path


def get_db_path():
    return get_data_path('db')


def get_downloads_xml_path():
    return get_data_path('downloads-xml')


def get_downloads_csv_path():
    return get_data_path('downloads-csv')
