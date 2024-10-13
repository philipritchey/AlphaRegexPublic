'''
test Literal()
'''
import pytest
from main.partial_regex import PartialRegexNodeType, Literal

def test_literal():
  '''
  test Literal()
  '''
  literal = Literal('x')
  assert literal.type == PartialRegexNodeType.LITERAL
  assert literal.literal == 'x'

def test_literal_too_long():
  '''test Literal() with an invalid symbol'''
  with pytest.raises(ValueError):
    Literal('ab')
