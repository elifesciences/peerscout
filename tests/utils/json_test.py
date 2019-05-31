from datetime import datetime, date
import uuid

import pytest

from peerscout.utils.json import CustomJSONEncoder


class TestCustomJSONEncoder:
    def test_should_encode_set(self):
        assert CustomJSONEncoder().encode({1, 2, 3}) == '[1, 2, 3]'

    def test_should_encode_date(self):
        assert CustomJSONEncoder().encode(date(2001, 2, 3)) == '"2001-02-03"'

    def test_should_encode_datetime(self):
        assert CustomJSONEncoder().encode(datetime(2001, 2, 3, 4, 5, 6)) == '"2001-02-03T04:05:06"'

    def test_should_encode_uuid_using_base_flask_encoder(self):
        x = uuid.uuid4()
        assert CustomJSONEncoder().encode(x) == '"%s"' % str(x)

    def test_should_encode_string_using_default_encoder(self):
        assert CustomJSONEncoder().encode('123') == '"123"'

    def test_should_encode_dict_using_default_encoder(self):
        assert CustomJSONEncoder().encode({'key': '123'}) == '{"key": "123"}'

    def test_should_raise_type_error_for_custom_object(self):
        class CustomObject:
            def __init__(self, x):
                self.x = x
        with pytest.raises(TypeError):
            CustomJSONEncoder().encode(CustomObject('123'))
