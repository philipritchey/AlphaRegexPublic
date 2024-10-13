'''
test Hole()
'''
from main.partial_regex import PartialRegexNodeType, Hole

def test_hole():
  '''
  test Hole()
  '''
  hole = Hole()
  assert hole.type == PartialRegexNodeType.HOLE

