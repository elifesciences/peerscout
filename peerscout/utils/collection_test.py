from .collection import (
  force_list
)

class TestForceList:
  def test_should_return_empty_list_if_arg_is_none(self):
    assert force_list(None) == []

  def test_should_return_list_unchanged(self):
    assert force_list([1, 2, 3]) == [1, 2, 3]

  def test_should_return_list_with_single_item_if_arg_is_not_list(self):
    assert force_list(1) == [1]
