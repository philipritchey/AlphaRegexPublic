'''
test EmptyLanguage()
'''
from main.partial_regex import PartialRegexNodeType, EmptyLanguage

def test_empty_language():
  '''
  test EmptyLanguage()
  '''
  empty = EmptyLanguage()
  assert empty.type == PartialRegexNodeType.EMPTY_LANGUAGE
