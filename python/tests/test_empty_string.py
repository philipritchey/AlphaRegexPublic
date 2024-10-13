'''
test EmptyString()
'''

from main.partial_regex import PartialRegexNodeType, EmptyString

def test_empty_string():
  '''
  test EmptyString()
  '''
  empty = EmptyString()
  assert empty.type == PartialRegexNodeType.EMPTY_STRING
