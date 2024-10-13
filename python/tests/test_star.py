'''
test Star()
'''
from main.partial_regex import PartialRegexNodeType, Star

def test_star():
  '''
  test Star()
  '''
  s = Star()
  assert s.type == PartialRegexNodeType.STAR
  assert s.left.type == PartialRegexNodeType.HOLE
