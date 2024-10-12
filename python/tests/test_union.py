from main.partial_regex import PartialRegexNodeType, Union

def test_union():
  s = Union()
  assert s.type == PartialRegexNodeType.UNION
  assert s.left.type == PartialRegexNodeType.HOLE
  assert s.right.type == PartialRegexNodeType.HOLE
