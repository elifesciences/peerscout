from unittest.mock import Mock
from concurrent.futures import ThreadPoolExecutor

from .threading import (
    lazy_thread_local
)


def _run_in_thread(callable_):
    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(callable_).result()


class TestLazyThreadLocal:
    def test_should_not_call_creator_if_not_called(self):
        creator = Mock()
        lazy_thread_local(creator)
        assert not creator.called

    def test_should_return_value_from_getter(self):
        creator = Mock()
        lazy_getter = lazy_thread_local(creator)
        result = _run_in_thread(lazy_getter)
        assert result == creator.return_value

    def test_should_call_creator_once_if_called_multiple_times_in_same_thread(self):
        creator = Mock()
        lazy_getter = lazy_thread_local(creator)
        result = _run_in_thread(lambda: (lazy_getter(), lazy_getter()))
        assert result == (creator.return_value, creator.return_value)
        assert creator.call_count == 1

    def test_should_call_creator_multiple_times_in_separate_threads(self):
        creator = Mock()
        lazy_getter = lazy_thread_local(creator)
        result = (
            _run_in_thread(lazy_getter),
            _run_in_thread(lazy_getter)
        )
        assert result == (creator.return_value, creator.return_value)
        assert creator.call_count == 2
