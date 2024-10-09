import pytest
from main.partial_regex import PartialRegexNode, PartialRegexNodeType, Literal, Union, Concatenation, Star, Hole, EmptyLanguage, EmptyString

def test_concat_literals():
    s1 = Literal('a')
    s2 = Literal('b')
    s3 = s1 * s2
    assert s3.type == PartialRegexNodeType.CONCATENATION
    assert s3.left.literal == 'a'
    assert s3.right.literal == 'b'

def test_union_literals():
    s1 = Literal('a')
    s2 = Literal('b')
    s3 = s1 + s2
    assert s3.type == PartialRegexNodeType.UNION
    assert s3.left.literal == 'a'
    assert s3.right.literal == 'b'

def test_copy():
    s1 = Literal('a')
    s2 = s1.copy()
    assert s2.type == PartialRegexNodeType.LITERAL
    assert s2.literal == 'a'
    assert s2.left is None
    assert s2.right is None

def test_fill_hole():
    hole = Hole()
    s1 = Literal('a')
    s2 = hole.fill(s1)
    assert s2.type == PartialRegexNodeType.LITERAL

def test_fill_hole_2():
    hole = Hole()
    s1 = Literal('a') * hole
    s2 = s1.fill(Literal('b'))
    assert s2.type == PartialRegexNodeType.CONCATENATION
    assert s2.left.type == PartialRegexNodeType.LITERAL
    assert s2.left.literal == 'a'
    assert s2.right.type == PartialRegexNodeType.LITERAL
    assert s2.right.literal == 'b'

def test_fill_hole_by_index():
    s1 = Hole()
    s2 = s1.fill(Literal('x'), 0)
    assert s1.type == PartialRegexNodeType.HOLE
    assert s2.type == PartialRegexNodeType.LITERAL
    assert s2.literal == 'x'

def test_fill_hole_by_index_2():
    s1 = Hole() * Hole()
    s2 = s1.fill(Literal('x'), 1)
    assert s1.type == PartialRegexNodeType.CONCATENATION
    assert s1.left.type == PartialRegexNodeType.HOLE
    assert s1.right.type == PartialRegexNodeType.HOLE
    assert s2.left.type == PartialRegexNodeType.HOLE
    assert s2.right.type == PartialRegexNodeType.LITERAL
    assert s2.right.literal == 'x'

def test_fill_no_hole():
    s = Literal('a')
    with pytest.raises(ValueError):
        s.fill(Literal('b'))

def test_fill_hole_with_concat_holes():
    s = Hole().fill(Concatenation())
    assert s.type == PartialRegexNodeType.CONCATENATION
    assert s.left.type == PartialRegexNodeType.HOLE
    assert s.right.type == PartialRegexNodeType.HOLE

def test_fill_hole_with_union_holes():
    s = Hole().fill(Union())
    assert s.type == PartialRegexNodeType.UNION
    assert s.left.type == PartialRegexNodeType.HOLE
    assert s.right.type == PartialRegexNodeType.HOLE

def test_fill_hole_with_star_hole():
    s = Hole().fill(Star())
    assert s.type == PartialRegexNodeType.STAR
    assert s.left.type == PartialRegexNodeType.HOLE
    assert s.right is None

def test_literal_too_long():
    with pytest.raises(ValueError):
        PartialRegexNode(PartialRegexNodeType.LITERAL, 'ab')

def test_literal_to_string():
    s = Literal('b')
    assert str(s) == 'b'

def test_concatenation_to_string():
    s1 = Literal('a')
    s2 = Literal('b')
    s3 = s1 * s2
    assert str(s3) == 'ab'

def test_concatenation_to_string_2():
    s1 = Literal('a')
    s2 = Literal('b')
    s3 = Literal('c')
    s4 = Literal('d')
    s5 = s1 * s2
    s6 = s3 * s4
    s7 = s5 * s6
    assert str(s7) == 'abcd'

def test_union_to_string():
    s1 = Literal('a')
    s2 = Literal('b')
    s3 = s1 + s2
    assert str(s3) == '(a|b)'

def test_hole_to_string():
    s = Hole()
    assert str(s) == str(PartialRegexNodeType.HOLE)

def test_star_to_string():
    s = Star()
    assert str(s) == f'({PartialRegexNodeType.HOLE})*'

def test_concatentation_with_empty_string_to_string():
    s1 = Literal('a')
    s2 = EmptyString()
    s3 = s1 * s2
    assert str(s3) == 'a'
    s4 = s2 * s1
    assert str(s4) == 'a'

def test_concatentation_with_empty_language_to_string():
    s1 = Literal('a')
    s2 = EmptyLanguage()
    s3 = s1 * s2
    assert str(s3) == str(PartialRegexNodeType.EMPTY_LANGUAGE)
    s4 = s2 * s1
    assert str(s4) == str(PartialRegexNodeType.EMPTY_LANGUAGE)

def test_union_with_empty_string_to_string():
    s1 = Literal('a')
    s2 = EmptyString()
    s3 = s1 + s2
    assert str(s3) == 'a?'
    s4 = s2 + s1
    assert str(s4) == 'a?'

def test_union_with_empty_string_to_string_2():
    s1 = Literal('a') * Literal('b')
    s2 = EmptyString()
    s3 = s1 + s2
    assert str(s3) == '(ab)?'
    s4 = s2 + s1
    assert str(s4) == '(ab)?'

def test_union_with_empty_language_to_string():
    s1 = Literal('a')
    s2 = EmptyLanguage()
    s3 = s1 + s2
    assert str(s3) == 'a'
    s4 = s2 + s1
    assert str(s4) == 'a'

def test_union_with_empty_langauge_to_string_2():
    s1 = Literal('a') * Literal('b')
    s2 = EmptyLanguage()
    s3 = s1 + s2
    assert str(s3) == 'ab'
    s4 = s2 + s1
    assert str(s4) == 'ab'

def test_empty_string_to_string():
    assert str(EmptyString()) == str(PartialRegexNodeType.EMPTY_STRING)

def test_empty_language_to_string():
    assert str(EmptyLanguage()) == str(PartialRegexNodeType.EMPTY_LANGUAGE)

def test_empty_string_star_to_string():
    s = Star()
    s.left = EmptyString()
    assert str(s) == str(PartialRegexNodeType.EMPTY_STRING)

def test_empty_language_star_to_string():
    s = Star()
    s.left = EmptyLanguage()
    assert str(s) == str(PartialRegexNodeType.EMPTY_LANGUAGE)

def test_repstar_to_string():
    s = Star()
    s.left = Star()
    s.left.left = Literal('a')
    assert str(s) == '(a)*'

    s.left.left = Star()
    s.left.left.left = Literal('a')
    assert str(s) == '(a)*'

def test_count_holes():
    s = ((Hole() * Hole()) + (Hole() * Hole())) + (Literal('a') * (Literal('b') + Hole()))
    assert s.holes() == 5

def test_state_expansion():
    s = Hole()
    literals = '.01'
    states = s.next_states(literals)
    # ., 0, 1, empty string, empty language, [][], []|[], []*
    assert len(states) == 8
    for literal in literals:
        assert Literal(literal) in states
    assert EmptyString() in states
    assert EmptyLanguage() in states
    assert Concatenation() in states
    assert Union() in states
    assert Star() in states

def test_state_expansion_2():
    s = Hole() * Hole()
    literals = '.abc'
    states = s.next_states(literals)
    assert len(states) == 18
    for literal in literals:
        assert Literal(literal) * Hole() in states
        assert Hole() * Literal(literal) in states
    assert EmptyString() * Hole() in states
    assert EmptyLanguage() * Hole() in states
    assert Concatenation() * Hole() in states
    assert Union() * Hole() in states
    assert Star() * Hole() in states
    assert Hole() * EmptyString() in states
    assert Hole() * EmptyLanguage() in states
    assert Hole() * Concatenation() in states
    assert Hole() * Union() in states
    assert Hole() * Star() in states
    
def test_ordering():
    empty = EmptyString()
    hole = Hole()
    union = Union()
    assert empty < hole
    assert hole < union

def test_cost():
    literal = Literal('a')
    empty_string = EmptyString()
    empty_language = EmptyLanguage()
    union = Union()
    concatentation = Concatenation()
    star = Star()
    hole = Hole()
    assert literal.cost() == empty_string.cost()
    assert literal.cost() == empty_language.cost()
    assert union.cost() > concatentation.cost()
    assert hole.cost() > star.cost() - hole.cost()
    assert hole.cost() > union.cost() - 2 * hole.cost()
    assert hole.cost() > concatentation.cost() - 2 * hole.cost()
    assert hole.cost() > literal.cost()

def test_overapproximation():
    assert Literal('a').overapproximation() == Literal('a')
    assert EmptyString().overapproximation() == EmptyString()
    assert EmptyLanguage().overapproximation() == EmptyLanguage()
    assert Union().overapproximation() == Hole().overapproximation() + Hole().overapproximation()
    assert Concatenation().overapproximation() == Hole().overapproximation() * Hole().overapproximation()
    dot_star = Star()
    dot_star.left = Literal('.')
    assert Hole().overapproximation() == dot_star
    assert dot_star.overapproximation() == dot_star
    
def test_underapproximation():
    assert Literal('a').underapproximation() == Literal('a')
    assert EmptyString().underapproximation() == EmptyString()
    assert EmptyLanguage().underapproximation() == EmptyLanguage()
    assert Union().underapproximation() == Hole().underapproximation() + Hole().underapproximation()
    assert Concatenation().underapproximation() == Hole().underapproximation() * Hole().underapproximation()
    assert Hole().underapproximation() == EmptyLanguage()
    dot_star = Star()
    dot_star.left = Literal('.')
    assert dot_star.underapproximation() == dot_star
    
def test_approximations_with_unknown_type():
    s = PartialRegexNode(PartialRegexNodeType.OPTIONAL)
    with pytest.raises(ValueError):
        s.overapproximation()
    with pytest.raises(ValueError):
        s.underapproximation()
        
def test_hash():
    s1 = EmptyString()
    s2 = Star()
    s2.left = EmptyString()
    assert hash(s1) == hash(s2)

def test_eq():
    s1 = EmptyString()
    s2 = Star()
    s2.left = EmptyString()
    assert s1 == s2

def test_split_of_unroll():
    state = Union(Literal('1'), Hole())
    unrolled_state = state.unroll()
    assert unrolled_state == state
    split_of_unrolled_state = unrolled_state.split()
    assert len(split_of_unrolled_state) == 2
    assert Literal('1') in split_of_unrolled_state
    assert Hole() in split_of_unrolled_state

    state = Star(Literal('e'))
    unrolled_state = state.unroll()
    assert str(unrolled_state) == 'ee(e)*'
    split_of_unrolled_state = unrolled_state.split()
    assert len(split_of_unrolled_state) == 1
    state = split_of_unrolled_state.pop()
    assert str(state) == 'ee(e)*'
    assert repr(state) == "Concatenation(Concatenation(Literal('e'), Literal('e')), Star(Literal('e')))"

def test_repr():
    assert(repr(Union(EmptyLanguage()))) == "Union(EmptyLanguage(), Hole())"
    assert(repr(EmptyString())) == 'EmptyString()'

def test_unroll():
    assert EmptyString().unroll() == EmptyString()
    assert EmptyLanguage().unroll() == EmptyLanguage()
    with pytest.raises(ValueError):
        PartialRegexNode(PartialRegexNodeType.OPTIONAL).unroll()

def test_split():
    assert EmptyLanguage().split() == {EmptyLanguage()}
    assert EmptyString().split() == {EmptyString()}
    with pytest.raises(ValueError):
        PartialRegexNode(PartialRegexNodeType.OPTIONAL).split()