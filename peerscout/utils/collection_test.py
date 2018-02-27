from .collection import (
  force_list,
  invert_set_dict
)

class TestForceList:
  def test_should_return_empty_list_if_arg_is_none(self):
    assert force_list(None) == []

  def test_should_return_list_unchanged(self):
    assert force_list([1, 2, 3]) == [1, 2, 3]

  def test_should_return_list_with_single_item_if_arg_is_not_list(self):
    assert force_list(1) == [1]

class TestInvertSetDict:
  def test_should_return_empty_dict_for_empty_dict(self):
    assert invert_set_dict({}) == {}

  def test_should_return_invert_and_merge_values(self):
    assert invert_set_dict({'a': {1, 2}, 'b': {1, 3}}) == {1: {'a', 'b'}, 2: {'a'}, 3: {'b'}}
