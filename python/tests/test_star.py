from main.partial_regex import PartialRegexNodeType, Star

def test_star():
  s = Star()
  assert s.type == PartialRegexNodeType.STAR
  assert s.left.type == PartialRegexNodeType.HOLE
