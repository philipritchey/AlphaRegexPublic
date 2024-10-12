from main.partial_regex import PartialRegexNodeType, EmptyLanguage

def test_empty_language():
  empty = EmptyLanguage()
  assert empty.type == PartialRegexNodeType.EMPTY_LANGUAGE
