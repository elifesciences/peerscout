from .import_utils import (
  parse_comma_separated_list,
  comma_separated_column_to_map,
  _hack_split_and_fix_double_quote_encoding_issue_in_line
)

KEY_1 = 'key1'
KEY_2 = 'key2'

VALUE_1 = 'value1'
VALUE_2 = 'value2'

class TestParseCommaSeparatedList:
  def test_should_return_empty_list_for_empty_string(self):
    assert parse_comma_separated_list('') == []

  def test_should_return_empty_list_for_blank_string(self):
    assert parse_comma_separated_list(' ') == []

  def test_should_return_multiple_values_separated_by_comma(self):
    assert parse_comma_separated_list('%s,%s' % (VALUE_1, VALUE_2)) == [VALUE_1, VALUE_2]

  def test_should_return_strip_space_around_values(self):
    assert parse_comma_separated_list(' %s , %s ' % (VALUE_1, VALUE_2)) == [VALUE_1, VALUE_2]

class TestCommaSeparatedColumnToMap:
  def test_should_create_map_with_multiple_values(self):
    assert comma_separated_column_to_map([KEY_1], ['%s,%s' % (VALUE_1, VALUE_2)]) == {
      KEY_1: [VALUE_1, VALUE_2]
    }

  def test_should_create_map_with_multiple_keys(self):
    assert comma_separated_column_to_map([KEY_1, KEY_2], [VALUE_1, VALUE_2]) == {
      KEY_1: [VALUE_1],
      KEY_2: [VALUE_2]
    }

class TestHackSplitAndFixDoubleQuoteEncodingIssueInLine:
  def test_should_return_simple_tokens(self):
    assert list(_hack_split_and_fix_double_quote_encoding_issue_in_line(
      'value1,value2'
    )) == ['value1', 'value2']

  def test_should_return_quoted_tokens(self):
    assert list(_hack_split_and_fix_double_quote_encoding_issue_in_line(
      '"value1","value2"'
    )) == ['"value1"', '"value2"']

  def test_should_escape_quotes_not_followed_by_a_comma_or_end_at_end_of_value(self):
    assert list(_hack_split_and_fix_double_quote_encoding_issue_in_line(
      '"value1","value2 "quoted"","value3"'
    )) == ['"value1"', '"value2 ""quoted"""', '"value3"']

  def test_should_escape_quotes_not_followed_by_a_comma_or_end_middle_of_value(self):
    assert list(_hack_split_and_fix_double_quote_encoding_issue_in_line(
      '"value1","value2 "quoted", value3"'
    )) == ['"value1"', '"value2 ""quoted"", value3"']
