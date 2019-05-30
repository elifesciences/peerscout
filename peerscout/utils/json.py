from datetime import date

from flask.json import JSONEncoder as _JSONEncoder


class CustomJSONEncoder(_JSONEncoder):
    def default(self, obj):  # pylint: disable=method-hidden, arguments-differ
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            if isinstance(obj, set):
                return list(obj)
        except TypeError:
            pass
        return _JSONEncoder.default(self, obj)
