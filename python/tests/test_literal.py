import pytest
from main.partial_regex import PartialRegexNodeType, Literal

def test_literal():
    literal = Literal('x')
    assert literal.type == PartialRegexNodeType.LITERAL
    assert literal.literal == 'x'

def test_literal_too_long():
    with pytest.raises(ValueError):
        Literal('ab')
    