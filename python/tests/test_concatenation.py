'''
test Concatenation()
'''

from main.partial_regex import PartialRegexNodeType, Concatenation

def test_concatentation():
  '''
  test Concatenation()
  '''
  s = Concatenation()
  assert s.type == PartialRegexNodeType.CONCATENATION
  assert s.left.type == PartialRegexNodeType.HOLE
  assert s.right.type == PartialRegexNodeType.HOLE
