from flask import Flask
from werkzeug.datastructures import MultiDict

from peerscout.server.auth.FlaskAuth0 import (
    get_remote_ip,
    parse_allowed_ips
)

app = Flask(__name__)

IP1 = '172.0.0.101'
IP2 = '172.0.0.102'
OTHER = 'other'


class TestGetRemoteIp:
    def test_should_return_remote_addr_if_no_x_forwarded_for(self):
        with app.test_request_context(environ_base={'REMOTE_ADDR': IP1}):
            assert get_remote_ip() == IP1

    def test_should_return_x_forwarded_for_if_exists(self):
        with app.test_request_context(headers={'X-Forwarded-For': IP2}):
            assert get_remote_ip() == IP2

    def test_should_return_first_value_of_x_forwarded_for_if_exists(self):
        headers = MultiDict()
        headers.add('X-Forwarded-For', IP2)
        headers.add('X-Forwarded-For', OTHER)
        with app.test_request_context(headers=headers):
            assert get_remote_ip() == IP2


class TestParseAllowedIps:
    def test_should_parse_domains_as_lower_case(self):
        allowed_ips = parse_allowed_ips('127.0.0.1')
        assert allowed_ips == {'127.0.0.1'}

    def test_parse_multiple_emails(self):
        allowed_ips = parse_allowed_ips('127.0.0.1,127.0.0.2')
        assert allowed_ips == {'127.0.0.1', '127.0.0.2'}

    def test_should_ignore_blank_domains(self):
        allowed_ips = parse_allowed_ips('127.0.0.1,,127.0.0.2')
        assert allowed_ips == {'127.0.0.1', '127.0.0.2'}

    def test_should_ignore_space_around_domains(self):
        allowed_ips = parse_allowed_ips(' 127.0.0.1 , 127.0.0.2 ')
        assert allowed_ips == {'127.0.0.1', '127.0.0.2'}
