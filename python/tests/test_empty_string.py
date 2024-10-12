from main.partial_regex import PartialRegexNodeType, EmptyString

def test_empty_string():
  empty = EmptyString()
  assert empty.type == PartialRegexNodeType.EMPTY_STRING
