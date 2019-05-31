from unittest.mock import Mock

from peerscout.server.auth.Auth0 import Auth0

EMAIL = 'user1@domain.org'
DOMAIN = 'test.auth0.com'

USER_INFO = {
    'email': EMAIL
}

AUTHORIZED_RESULT = 'authorized'
NOT_AUTHORIZED_RESULT = 'not-authorized'
ACCESS_TOKEN = 'access1'


def GET_USER_INFO(_):
    return USER_INFO


def REQUEST_HANDLER(email=None):  # pylint: disable=unused-argument
    return AUTHORIZED_RESULT


def NOT_AUTHORIZED_HANDLER():
    return NOT_AUTHORIZED_RESULT


def GET_ACCESS_TOKEN():
    return ACCESS_TOKEN


def _default_is_valid_email(email):
    return email == EMAIL


def _create_auth0(get_user_info, is_valid_email=None):
    if is_valid_email is None:
        is_valid_email = _default_is_valid_email
    auth0 = Auth0(domain=DOMAIN, is_valid_email=is_valid_email)
    auth0.get_user_info = get_user_info
    return auth0


def _raise(e):
    raise e


def test_should_call_function_if_access_token_is_valid():
    auth0 = _create_auth0(GET_USER_INFO)
    result = auth0.wrap_request_handler(
        REQUEST_HANDLER, GET_ACCESS_TOKEN, NOT_AUTHORIZED_HANDLER
    )()
    assert result == AUTHORIZED_RESULT


def test_should_pass_valid_email_to_request_handler():
    auth0 = _create_auth0(GET_USER_INFO)
    request_handler = Mock()
    auth0.wrap_request_handler(
        request_handler, GET_ACCESS_TOKEN, NOT_AUTHORIZED_HANDLER
    )()
    request_handler.assert_called_with(email=EMAIL)


def test_should_call_function_if_access_token_is_none():
    auth0 = _create_auth0(GET_USER_INFO)
    result = auth0.wrap_request_handler(
        REQUEST_HANDLER, lambda: None, NOT_AUTHORIZED_HANDLER
    )()
    assert result == NOT_AUTHORIZED_RESULT


def test_should_call_function_if_access_token_is_invalid():
    auth0 = _create_auth0(lambda _: _raise(Exception('not authorized')))
    result = auth0.wrap_request_handler(
        REQUEST_HANDLER, GET_ACCESS_TOKEN, NOT_AUTHORIZED_HANDLER
    )()
    assert result == NOT_AUTHORIZED_RESULT


def test_should_call_function_if_email_is_invalid():
    auth0 = _create_auth0(USER_INFO, is_valid_email=lambda _: False)
    result = auth0.wrap_request_handler(
        REQUEST_HANDLER, GET_ACCESS_TOKEN, NOT_AUTHORIZED_HANDLER
    )()
    assert result == NOT_AUTHORIZED_RESULT


def test_should_call_function_if_access_token_is_none_but_authorization_is_not_required():
    auth0 = _create_auth0(GET_USER_INFO)
    result = auth0.wrap_request_handler(
        REQUEST_HANDLER, lambda: None, NOT_AUTHORIZED_HANDLER,
        requires_auth=lambda: False
    )()
    assert result == AUTHORIZED_RESULT


def test_should_pass_keyword_arguments_to_request_handler_if_authorizing():
    auth0 = _create_auth0(GET_USER_INFO)
    request_handler = Mock()
    auth0.wrap_request_handler(
        request_handler, GET_ACCESS_TOKEN, NOT_AUTHORIZED_HANDLER
    )(other='123')
    request_handler.assert_called_with(email=EMAIL, other='123')


def test_should_pass_keyword_arguments_to_request_handler_if_not_authorizing():
    auth0 = _create_auth0(GET_USER_INFO)
    request_handler = Mock()
    auth0.wrap_request_handler(
        request_handler, GET_ACCESS_TOKEN, NOT_AUTHORIZED_HANDLER,
        requires_auth=lambda: False
    )(other='123')
    request_handler.assert_called_with(other='123')
