from main.partial_regex import PartialRegexNodeType, Hole

def test_new_hole():
    hole = Hole()
    assert hole.type == PartialRegexNodeType.HOLE

