'''
tests for partial_regex.py
'''
import pytest
from main.partial_regex import PartialRegexNode, PartialRegexNodeType, Literal, Union, Concatenation, Star, Hole, EmptyLanguage, EmptyString, opt, ZeroOrOne, opt_concatentation, opt_optional, opt_star, opt_union

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
  assert str(opt(s3)) == 'a'
  s4 = s2 * s1
  assert str(opt(s4)) == 'a'

def test_concatentation_with_empty_language_to_string():
  s1 = Literal('a')
  s2 = EmptyLanguage()
  s3 = s1 * s2
  assert str(opt(s3)) == str(PartialRegexNodeType.EMPTY_LANGUAGE)
  s4 = s2 * s1
  assert str(opt(s4)) == str(PartialRegexNodeType.EMPTY_LANGUAGE)

def test_union_with_empty_string_to_string():
  s1 = Literal('a')
  s2 = EmptyString()
  s3 = s1 + s2
  assert str(opt(s3)) == 'a?'
  s4 = s2 + s1
  assert str(opt(s4)) == 'a?'

def test_union_with_empty_string_to_string_2():
  s1 = Literal('a') * Literal('b')
  s2 = EmptyString()
  s3 = s1 + s2
  assert str(opt(s3)) == '(ab)?'
  s4 = s2 + s1
  assert str(opt(s4)) == '(ab)?'

def test_union_with_empty_language_to_string():
  s1 = Literal('a')
  s2 = EmptyLanguage()
  s3 = s1 + s2
  assert str(opt(s3)) == 'a'
  s4 = s2 + s1
  assert str(opt(s4)) == 'a'

def test_union_with_empty_langauge_to_string_2():
  s1 = Literal('a') * Literal('b')
  s2 = EmptyLanguage()
  s3 = s1 + s2
  assert str(opt(s3)) == 'ab'
  s4 = s2 + s1
  assert str(opt(s4)) == 'ab'

def test_empty_string_to_string():
  assert str(EmptyString()) == str(PartialRegexNodeType.EMPTY_STRING)

def test_empty_language_to_string():
  assert str(EmptyLanguage()) == str(PartialRegexNodeType.EMPTY_LANGUAGE)

def test_empty_string_star_to_string():
  s = Star()
  s.left = EmptyString()
  assert str(opt(s)) == str(PartialRegexNodeType.EMPTY_STRING)

def test_empty_language_star_to_string():
  s = Star()
  s.left = EmptyLanguage()
  assert str(opt(s)) == str(PartialRegexNodeType.EMPTY_LANGUAGE)

def test_repstar_to_string():
  s = Star()
  s.left = Star()
  s.left.left = Literal('a')
  assert str(opt(s)) == 'a*'

  s.left.left = Star()
  s.left.left.left = Literal('a')
  assert str(opt(s)) == 'a*'

def test_count_holes():
  s = ((Hole() * Hole()) + (Hole() * Hole())) + (Literal('a') * (Literal('b') + Hole()))
  assert s.holes() == 5

def test_state_expansion():
  s = Hole()
  alphabet = '01'
  states = s.next_states(alphabet)
  # ., 0, 1, empty string, empty language, [][], []|[], []*
  assert len(states) == 8
  for literal in alphabet + '.':
    assert Literal(literal) in states
  assert EmptyString() in states
  assert EmptyLanguage() in states
  assert Concatenation() in states
  assert Union() in states
  assert Star() in states

def test_state_expansion_2():
  s = Hole() * Hole()
  alphabet = 'abc'
  states = s.next_states(alphabet)
  assert len(states) == 9
  for literal in alphabet + '.':
    assert Literal(literal) * Hole() in states
    # assert Hole() * Literal(literal) in states
  assert EmptyString() * Hole() in states
  assert EmptyLanguage() * Hole() in states
  assert Concatenation() * Hole() in states
  assert Union() * Hole() in states
  assert Star() * Hole() in states
  # assert Hole() * EmptyString() in states
  # assert Hole() * EmptyLanguage() in states
  # assert Hole() * Concatenation() in states
  # assert Hole() * Union() in states
  # assert Hole() * Star() in states

def test_state_expansion_of_star_of_hole():
  s = Star(Hole())
  alphabet = '01'
  states = s.next_states(alphabet)
  assert len(states) == 7
  for literal in alphabet + '.':
    assert Star(Literal(literal)) in states
  assert Star(EmptyString()) in states
  assert Star(EmptyLanguage()) in states
  assert Star(Concatenation()) in states
  assert Star(Union()) in states
  assert Star(Star()) not in states

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
  s = PartialRegexNode(PartialRegexNodeType.PLUS)
  with pytest.raises(ValueError):
    s.overapproximation()
  with pytest.raises(ValueError):
    s.underapproximation()

def test_hash():
  s1 = EmptyString()
  s2 = Star()
  s2.left = EmptyString()
  assert hash(s1) == hash(opt(s2))

  assert hash(Star(Literal('0'))) == hash(Star(Literal('0')))

  assert hash(Star(Literal('1'))) != hash(Literal('0'))
  assert hash(Star(Literal('1'))) != hash(Literal('1'))
  assert hash(Star(Literal('1'))) != hash(Literal('.'))
  assert hash(Star(Literal('1'))) != hash(EmptyString())
  assert hash(Star(Literal('1'))) != hash(EmptyLanguage())
  assert hash(Star(Literal('1'))) != hash(Star())
  assert hash(Star(Literal('1'))) != hash(Concatenation())
  assert hash(Star(Literal('1'))) != hash(Union())
  assert hash(Star(Literal('1'))) != hash(Star(Literal('0')))


def test_eq():
  s1 = EmptyString()
  s2 = Star()
  s2.left = EmptyString()
  assert s1 == opt(s2)

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
  assert str(unrolled_state) == 'eee*'
  split_of_unrolled_state = unrolled_state.split()
  assert len(split_of_unrolled_state) == 1
  state = split_of_unrolled_state.pop()
  assert str(state) == 'eee*'
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

def test_opt_concatenation():
  # e*e* -> e*
  assert opt(Concatenation(Star(Literal('e')), Star(Literal('e')))) == Star(Literal('e'))
  # (fe*)e* -> fe*
  assert opt(Concatenation(Concatenation(Literal('f'), Star(Literal('e'))), Star(Literal('e')))) == Concatenation(Literal('f'), Star(Literal('e')))
  # e*(e*f) -> e*f
  assert opt(Concatenation(Star(Literal('e')), Concatenation(Star(Literal('e')), Literal('f')))) == Concatenation(Star(Literal('e')), Literal('f'))
  # e*e? -> e*
  assert opt(Concatenation(Star(), ZeroOrOne())) == Star()
  # e?e* -> e*
  assert opt(Concatenation(ZeroOrOne(), Star())) == Star()
  # e1?(e1*e2) -> e1*e2
  assert opt(Concatenation(ZeroOrOne(Literal('e')), Concatenation(Star(Literal('e')), Literal('f')))) == Concatenation(Star(Literal('e')), Literal('f'))
  # e1*(e1?e2) -> e1*e2
  assert opt(Concatenation(Star(Literal('e')), Concatenation(ZeroOrOne(Literal('e')), Literal('f')))) == Concatenation(Star(Literal('e')), Literal('f'))
  # (e1e2*)e2? -> e1e2*
  assert opt(Concatenation(Concatenation(Literal('f'), Star(Literal('e'))), ZeroOrOne(Literal('e')))) == Concatenation(Literal('f'), Star(Literal('e')))
  # (e1e2?)e2* -> e1e2*
  assert opt(Concatenation(Concatenation(Literal('f'), ZeroOrOne(Literal('e'))), Star(Literal('e')))) == Concatenation(Literal('f'), Star(Literal('e')))
  # (e*e*)(e*e*) -> e*
  assert opt(Concatenation(Concatenation(Star(Literal('e')), Star(Literal('e'))), Concatenation(Star(Literal('e')), Star(Literal('e'))))) == Star(Literal('e'))

def test_opt_union():
  # e|e -> e
  assert opt(Union(Literal('e'), Literal('e'))) == Literal('e')
  # e|e* -> e*
  assert opt(Union(Literal('e'), Star(Literal('e')))) == Star(Literal('e'))
  # e*|e -> e*
  assert opt(Union(Star(Literal('e')), Literal('e'))) == Star(Literal('e'))
  # e|(e|f) -> e|f
  assert opt(Union(Literal('e'), Union(Literal('e'), Literal('f')))) == Union(Literal('e'), Literal('f'))
  # e|(f|e) -> e|f
  assert opt(Union(Literal('e'), Union(Literal('f'), Literal('e')))) == Union(Literal('e'), Literal('f'))
  # (e|f)|e -> e|f
  assert opt(Union(Union(Literal('e'), Literal('f')), Literal('e'))) == Union(Literal('e'), Literal('f'))
  # (f|e)|e -> f|e
  assert opt(Union(Union(Literal('f'), Literal('e')), Literal('e'))) == Union(Literal('f'), Literal('e'))
  # e*|(e|f) -> e*|f
  assert opt(Union(Star(Literal('e')), Union(Literal('e'), Literal('f')))) == Union(Star(Literal('e')), Literal('f'))
  # e*|(f|e) -> e*|f
  assert opt(Union(Star(Literal('e')), Union(Literal('f'), Literal('e')))) == Union(Star(Literal('e')), Literal('f'))
  # e|(e*|f) -> e*|f
  assert opt(Union(Literal('e'), Union(Star(Literal('e')), Literal('f')))) == Union(Star(Literal('e')), Literal('f'))
  # e|(f|e*) -> f|e*
  assert opt(Union(Literal('e'), Union(Literal('f'), Star(Literal('e'))))) == Union(Literal('f'), Star(Literal('e')))
  # (e|f)|e* -> f|e*
  assert opt(Union(Union(Literal('e'), Literal('f')), Star(Literal('e')))) == Union(Literal('f'), Star(Literal('e')))
  # (f|e)|e* -> f|e*
  assert opt(Union(Union(Literal('f'), Literal('e')), Star(Literal('e')))) == Union(Literal('f'), Star(Literal('e')))
  # (e*|f)|e -> e*|f
  assert opt(Union(Union(Star(Literal('e')), Literal('f')), Literal('e'))) == Union(Star(Literal('e')), Literal('f'))
  # (f|e*)|e -> f|e*
  assert opt(Union(Union(Literal('f'), Star(Literal('e'))), Literal('e'))) == Union(Literal('f'), Star(Literal('e')))
  # (e|e)|(e|e) -> e
  assert opt(Union(Union(Literal('e'), Literal('e')), Union(Literal('e'), Literal('e')))) == Literal('e')
  # (e|e)|(f|f) -> e|f
  assert opt(Union(Union(Literal('e'), Literal('e')), Union(Literal('f'), Literal('f')))) == Union(Literal('e'), Literal('f'))
  # e|e? -> e?
  assert opt(Union(Literal('e'), ZeroOrOne(Literal('e')))) == ZeroOrOne(Literal('e'))
  # (e2|f2)|e2? -> f2|e2?
  assert opt(Union(Union(Literal('a'), Literal('b')), ZeroOrOne(Literal('a')))) == Union(Literal('b'), ZeroOrOne(Literal('a')))
  # (f1|e2)|e2? -> f1|e2?
  assert opt(Union(Union(Literal('b'), Literal('a')), ZeroOrOne(Literal('a')))) == Union(Literal('b'), ZeroOrOne(Literal('a')))
  # e?|e -> e?
  assert opt(Union(ZeroOrOne(Literal('e')), Literal('e'))) == ZeroOrOne(Literal('e'))
  # e1?|(e1|f2) -> e1?|f2
  assert opt(Union(ZeroOrOne(Literal('e')), Union(Literal('e'), Literal('f')))) == Union(ZeroOrOne(Literal('e')), Literal('f'))
  # e1?|(f1|e1) -> e1?|f1
  assert opt(Union(ZeroOrOne(Literal('e')), Union(Literal('f'), Literal('e')))) == Union(ZeroOrOne(Literal('e')), Literal('f'))
  # (f1|e2?)|e2 -> f1|e2?
  assert opt(Union(Union(Literal('f'), ZeroOrOne(Literal('e'))), Literal('e'))) == Union(Literal('f'), ZeroOrOne(Literal('e')))
  # (e2?|f2)|e2 -> e2?|f2
  assert opt(Union(Union(ZeroOrOne(Literal('e')), Literal('f')), Literal('e'))) == Union(ZeroOrOne(Literal('e')), Literal('f'))
  # e1|(f1|e1?) -> f1|e1?
  assert opt(Union(Literal('e'), Union(Literal('f'), ZeroOrOne(Literal('e'))))) == Union(Literal('f'), ZeroOrOne(Literal('e')))
  # e1|(e1?|f2) -> e1?|f2
  assert opt(Union(Literal('e'), Union(ZeroOrOne(Literal('e')), Literal('f')))) == Union(ZeroOrOne(Literal('e')), Literal('f'))

  # not opt-able
  # (a|b)c*
  assert opt(Union(Union(Literal('a'), Literal('b')), Star(Literal('c')))) == Union(Union(Literal('a'), Literal('b')), Star(Literal('c')))
  # (a|b)|c?
  assert opt(Union(Union(Literal('a'), Literal('b')), ZeroOrOne(Literal('c')))) == Union(Union(Literal('a'), Literal('b')), ZeroOrOne(Literal('c')))
  # (ab)|c?
  assert opt(Union(Concatenation(Literal('a'), Literal('b')), ZeroOrOne(Literal('c')))) == Union(Concatenation(Literal('a'), Literal('b')), ZeroOrOne(Literal('c')))
  # a|(b|c)
  assert opt(Union(Literal('a'), Union(Literal('b'), Literal('c')))) == Union(Literal('a'), Union(Literal('b'), Literal('c')))
  # a?|(b|c)
  assert opt(Union(ZeroOrOne(Literal('a')), Union(Literal('b'), Literal('c')))) == Union(ZeroOrOne(Literal('a')), Union(Literal('b'), Literal('c')))
  # a*|(b|c)
  assert opt(Union(Star(Literal('a')), Union(Literal('b'), Literal('c')))) == Union(Star(Literal('a')), Union(Literal('b'), Literal('c')))

def test_opt_star():
  # e** -> e*
  assert opt(Star(Star(Literal('e')))) == Star(Literal('e'))
  # (ee*)* -> e*
  assert opt(Star(Concatenation(Literal('e'), Star(Literal('e'))))) == Star(Literal('e'))
  # (e*e)* -> e*
  assert opt(Star(Concatenation(Star(Literal('e')), Literal('e')))) == Star(Literal('e'))
  # (e**)* -> e*
  assert opt(Star(Star(Star(Literal('e'))))) == Star(Literal('e'))
  # e?* -> e*
  assert opt(Star(ZeroOrOne(Literal('e')))) == Star(Literal('e'))
  # (e?f?)* -> (e|f)*
  assert opt(Star(Concatenation(ZeroOrOne(Literal('e')), ZeroOrOne(Literal('f'))))) == Star(Union(Literal('e'), Literal('f')))
  # (e?e)* -> e*
  assert opt(Star(Concatenation(ZeroOrOne(Literal('e')), Literal('e')))) == Star(Literal('e'))
  # (ee?)* -> e*
  assert opt(Star(Concatenation(Literal('e'), ZeroOrOne(Literal('e'))))) == Star(Literal('e'))
  # (e*f*)* -> (e|f)*
  assert opt(Star(Concatenation(Star(Literal('e')), Star(Literal('f'))))) == Star(Union(Literal('e'), Literal('f')))

def test_opt_optional():
  # e?? -> e?
  assert opt(ZeroOrOne(ZeroOrOne(Literal('e')))) == ZeroOrOne(Literal('e'))
  # e*? -> e*
  assert opt(ZeroOrOne(Star(Literal('e')))) == Star(Literal('e'))
  # (ee*)? -> e*
  assert opt(ZeroOrOne(Concatenation(Literal('e'), Star(Literal('e'))))) == Star(Literal('e'))
  # (e*e)? -> e*
  assert opt(ZeroOrOne(Concatenation(Star(Literal('e')), Literal('e')))) == Star(Literal('e'))
  # ∅? -> ε
  assert opt(ZeroOrOne(EmptyLanguage())) == EmptyString()
  # ε? -> ε
  assert opt(ZeroOrOne(EmptyString())) == EmptyString()
  # (e*f*)? -> e*f*
  assert opt(ZeroOrOne(Concatenation(Star(Literal('e')), Star(Literal('f'))))) == Concatenation(Star(Literal('e')), Star(Literal('f')))
  # (e?f?)? -> e?f?
  assert opt(ZeroOrOne(Concatenation(ZeroOrOne(Literal('e')), ZeroOrOne(Literal('f'))))) == Concatenation(ZeroOrOne(Literal('e')), ZeroOrOne(Literal('f')))

  # (ef?)? -> (ef?)?
  assert opt(ZeroOrOne(Concatenation(Literal('e'), ZeroOrOne(Literal('f'))))) == ZeroOrOne(Concatenation(Literal('e'), ZeroOrOne(Literal('f'))))

def test_opt_multiple_repeat():
  state = Concatenation(Literal('.'), Union(EmptyString(), Union(EmptyString(), Hole())))
  overapproximation = state.overapproximation()
  opt2_overapproximation = opt(overapproximation)
  assert str(opt2_overapproximation) == '..*'

def test_empty_union_concat_to_str():
  state = Union(EmptyString(), Concatenation(Literal('a'), Literal('b')))
  assert str(state) == '(ab)?'

  state = Union(Concatenation(Literal('a'), Literal('b')), EmptyString())
  assert str(state) == '(ab)?'

def test_empty_union_union_to_str():
  state = Union(EmptyString(), Union(Literal('a'), Literal('b')))
  assert str(state) == '(a|b)?'

  state = Union(Union(Literal('a'), Literal('b')), EmptyString())
  assert str(state) == '(a|b)?'

def test_get_cost_of_optional():
  state = ZeroOrOne(Literal('a'))
  assert state.get_cost() > Literal('a').get_cost()

def test_get_depth():
  assert Hole().get_depth() == 1
  assert Star().get_depth() == 2
  assert ZeroOrOne().get_depth() == 2
  assert Concatenation().get_depth() == 2
  assert Union().get_depth() == 2
  assert Literal('a').get_depth() == 1

def test_overapproximation_of_optional():
  assert ZeroOrOne().overapproximation() == ZeroOrOne(Star(Literal('.')))

def test_underapproximation_of_optional():
  assert ZeroOrOne().underapproximation() == ZeroOrOne(EmptyLanguage())

def test_repr_optional():
  assert repr(ZeroOrOne()) == 'ZeroOrOne(Hole())'

def test_star_of_concat_stars_to_string():
  # (e*f*)* -> (e|f)*
  state = Star(Concatenation(Star(Literal('e')), Star(Literal('f'))))
  assert str(state) == '(e|f)*'

def test_opt_helpers_type_guard():
  state = Literal('a')
  assert opt_concatentation(state) == state
  assert opt_optional(state) == state
  assert opt_star(state) == state
  assert opt_union(state) == state

def test_opt_causing_multiple_repeat():
  state = Concatenation(Literal('.'), Union(EmptyString(), Union(EmptyString(), Star(Literal('.')))))
  o = opt(state)
  assert o == Concatenation(Literal('.'), Star(Literal('.')))

def test_cost_of_21():
  # solution to no21 in the paper: (0?1)*00(10?)*
  state1 = Star(ZeroOrOne(Literal('0')) * Literal('1')) * Literal('0') * Literal('0') * Star(Literal('1') * ZeroOrOne(Literal('0')))
  # solution my code found with same examples: (.(...|0))*
  state2 = Star(Literal('.') * Union(Literal('.') * Literal('.') * Literal('.'), Literal('0')))
  assert state2.cost() <= state1.cost()

def test_cost_of_10():
  # solution in paper: 1?(01)*0? = (1|λ)(01)*(0|λ)
  paper_soln = Concatenation(
    Concatenation(
      Union(
        Literal('1'),
        EmptyString()
      ),
      Star(
        Concatenation(
          Literal('0'),
          Literal('1')
        )
      )
    ),
    Union(
      Literal('0'),
      EmptyString()
    )
  )
  # solution my implementation finds: (0|λ)(1(0|(010*)*)|λ)
  my_soln = Concatenation(
    Union(
      Literal('0'),
      EmptyString()
    ),
    Union(
      Concatenation(
        Literal('1'),
        Union(
          Literal('0'),
          Star(
            Concatenation(
              Concatenation(
                Literal('0'),
                Literal('1')
              ),
              Star(
                Literal('0')
              )
            )
          )
        )
      ),
      EmptyString()
    )
  )
  # solution l-star finds: (1|01)*(0|λ)
  lstar_soln = Concatenation(
    Star(
      Union(
        Literal('1'),
        Concatenation(
          Literal('0'),
          Literal('1')
        )
      )
    ),
    Union(
      Literal('0'),
      EmptyString()
    )
  )
  # this is weird, it should find the cheaper solution first
  assert paper_soln.cost() == 89, f"got: {paper_soln.cost()}"
  assert my_soln.cost() == 142, f"got: {my_soln.cost()}"
  assert lstar_soln.cost() == 87, f"got: {lstar_soln.cost()}"

def test_cost_of_14():
  # solution in paper: (0+1(0+1))((0+1)(0+1))* = (0|1.)(..)*
  paper_soln = Concatenation(
    Union(
      Literal('0'),
      Concatenation(
        Literal('1'),
        Union(
          Literal('0'),
          Literal('1')
        )
      )
    ),
    Star(
      Concatenation(
        Union(
          Literal('0'),
          Literal('1')
        ),
        Union(
          Literal('0'),
          Literal('1')
        )
      )
    )
  )
  # solution lstar finds: (0|(1|0(0|1))((0|1)(0|1))*(0|1)) = 0|(1|0.)(..)*.
  lstar_soln = Union(
    Literal('0'),
    Concatenation(
      Concatenation(
        Union(
          Literal('1'),
          Concatenation(
            Literal('0'),
            Union(
              Literal('0'),
              Literal('1')
            )
          )
        ),
        Star(
          Concatenation(
            Union(
              Literal('0'),
              Literal('1')
            ),
            Union(
              Literal('0'),
              Literal('1')
            )
          )
        )
      ),
      Union(
        Literal('0'),
        Literal('1')
      )
    )
  )
  assert paper_soln.cost() == 151, f"got: {paper_soln.cost()}"
  assert lstar_soln.cost() == 215, f"got: {lstar_soln.cost()}"

def test_cost_of_22():
  # solution in paper: (0+1)(0+1)*1+(0+1)*0(0+1) = ..*1|.*0.
  paper_soln = Union(
    Concatenation(
      Concatenation(
        Union(Literal('0'), Literal('1')),
        Star(Union(Literal('0'), Literal('1')))
      ),
      Literal('1')
    ),
    Concatenation(
      Star(Union(Literal('0'), Literal('1'))),
      Concatenation(
        Literal('0'),
        Union(Literal('0'), Literal('1'))
      )
    )
  )
  # my solution (by hand): .*(0.|.1)
  my_soln = Concatenation(
    Star(Union(Literal('0'), Literal('1'))),
    Union(
      Concatenation(Literal('0'), Union(Literal('0'), Literal('1'))),
      Concatenation(Union(Literal('0'), Literal('1')), Literal('1'))
    )
  )
  # this is weird, it should find the cheaper solution first
  assert paper_soln.cost() == 204, f"got: {paper_soln.cost()}"
  assert my_soln.cost() == 151, f"got: {my_soln.cost()}"

def test_cost_no30():
  '''
  [] : 100
  []* : 120
  ([]|[])* : 250
  (0|[])* : 151
  (0|[][])* : 252
  (0|1[])* : 153
  (0|1.)* : 54
  '''
  assert Hole().cost() == 100
  assert Star().cost() == 120
  assert Star(Union()).cost() == 250
  assert Star(Union(Literal('0'), Hole())).cost() == 151
  assert Star(Union(Literal('0'), Concatenation())).cost() == 252
  assert Star(Union(Literal('0'), Concatenation(Literal('1'), Hole()))).cost() == 153
  assert Star(Union(Literal('0'), Concatenation(Literal('1'), Literal('.')))).cost() == 54

  '''
  [] : 100
  [][] : 201
  []*[] : 221
  0*[] : 122
  0*[]* : 142
  0*([][])* : 243
  0*(1[])* : 144
  0*(1[][])* : 245
  0*(1.[])* : 146
  0*(1.[]*)* : 166
  0*(1.0*)* : 67
  '''
  assert Hole().cost() == 100
  assert Concatenation().cost() == 201
  assert Concatenation(Star(), Hole()).cost() == 221
  assert Concatenation(Star(Literal('0')), Hole()).cost() == 122
  assert Concatenation(Star(Literal('0')), Star()).cost() == 142
  assert Concatenation(Star(Literal('0')), Star(Concatenation())).cost() == 243
  assert Concatenation(Star(Literal('0')), Star(Concatenation(Literal('1'), Hole()))).cost() == 144
  assert Concatenation(Star(Literal('0')), Star(Concatenation(Literal('1'), Concatenation()))).cost() == 245
  assert Concatenation(Star(Literal('0')), Star(Concatenation(Literal('1'), Concatenation(Literal('.'), Hole())))).cost() == 146
  assert Concatenation(Star(Literal('0')), Star(Concatenation(Literal('1'), Concatenation(Literal('.'), Star())))).cost() == 166
  assert Concatenation(Star(Literal('0')), Star(Concatenation(Literal('1'), Concatenation(Literal('.'), Star(Literal('0')))))).cost() == 67

def test_is_dead_no30():
  state = Star(Union(Literal('0'), Concatenation(Literal('1'), Hole())))
  P = {
    '',
    '101111',
    '1111',
    '10000',
    '010',
    '1000',
    '1110',
    '00',
    '011',
    '10010',
    '01100',
    '100',
    '0',
    '000',
    '11011',
    '00100',
    '11110',
    '1100',
    '00000',
    '0000',
    '01010',
    '00110',
    '0010',
    '01000',
    '110',
    '11000',
    '0110',
    '1010',
    '0011',
    '10110',
    '01111',
    '11100',
    '10011',
    '11',
    '01110',
    '1011',
    '001111',
    '00011',
    '00010',
    '11010',
    '10100',
    '0100',
    '10',
    '01011'
    }
  N = {
    '11111',
    '00011111',
    '11011111',
    '0011111',
    '00101',
    '0001',
    '101',
    '001',
    '1',
    '110111',
    '0111',
    '1101',
    '1011111',
    '10001',
    '00111',
    '10011111',
    '010111',
    '01001',
    '10111',
    '01101',
    '11101',
    '000111',
    '11001',
    '01',
    '111',
    '1001',
    '0101',
    '00001',
    '10101',
    '011111',
    '01011111',
    '100111'
    }
  assert not state.is_dead(P, N)
