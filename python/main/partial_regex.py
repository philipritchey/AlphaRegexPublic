'''
partial regex
'''

from enum import StrEnum
from functools import total_ordering
from typing import Self, Optional
from main.helpers import matches_all, matches_any

class PartialRegexNodeType(StrEnum):
  '''
  node types
  '''
  LITERAL = 'a'
  EMPTY_STRING = 'ε'
  EMPTY_LANGUAGE = '∅'
  CONCATENATION = '·'
  UNION = '|'
  STAR = '*'
  PLUS = '+'
  OPTIONAL = '?'
  HOLE = '□'

@total_ordering
class PartialRegexNode:
  '''
  a partial regex node (tree)
  '''
  def __init__(self,
               node_type: Optional[PartialRegexNodeType] = PartialRegexNodeType.HOLE,
               literal: Optional[str] = None):
    self.type = node_type
    self.left: Self = None
    self.right: Self = None
    self.literal: Optional[str] = None
    if node_type == PartialRegexNodeType.LITERAL:
      if len(literal) != 1:
        raise ValueError('length of literal must be exactly 1')
      self.literal = literal
    self._cost: int = -1

  def __eq__(self, other: Self) -> bool:
    return str(self) == str(other)

  def __hash__(self) -> int:
    return hash(str(self))

  def __lt__(self, other: Self) -> bool:
    return self.cost() < other.cost()

  def __mul__(self, other: Self) -> Self:
    s = PartialRegexNode(PartialRegexNodeType.CONCATENATION)
    s.left = self.copy()
    s.right = other.copy()
    return s

  def __add__(self, other: Self) -> Self:
    s = PartialRegexNode(PartialRegexNodeType.UNION)
    s.left = self.copy()
    s.right = other.copy()
    return s

  def __repr__(self) -> str:
    if self.type == PartialRegexNodeType.CONCATENATION:
      return f"Concatenation({repr(self.left)}, {repr(self.right)})"
    if self.type == PartialRegexNodeType.UNION:
      return f"Union({repr(self.left)}, {repr(self.right)})"
    if self.type == PartialRegexNodeType.HOLE:
      return 'Hole()'
    if self.type == PartialRegexNodeType.STAR:
      return f"Star({repr(self.left)})"
    if self.type == PartialRegexNodeType.OPTIONAL:
      return f"ZeroOrOne({repr(self.left)})"
    if self.type == PartialRegexNodeType.EMPTY_STRING:
      return 'EmptyString()'
    if self.type == PartialRegexNodeType.EMPTY_LANGUAGE:
      return 'EmptyLanguage()'
    return f"Literal('{self.literal}')"

  def __str__(self) -> str:
    if self.type == PartialRegexNodeType.CONCATENATION:
      if self.right.type == PartialRegexNodeType.EMPTY_STRING:
        return str(self.left)
      if self.left.type == PartialRegexNodeType.EMPTY_STRING:
        return str(self.right)
      if self.left.type == PartialRegexNodeType.EMPTY_LANGUAGE or self.right.type == PartialRegexNodeType.EMPTY_LANGUAGE:
        return str(PartialRegexNodeType.EMPTY_LANGUAGE)
      return f'{self.left}{self.right}'
    if self.type == PartialRegexNodeType.UNION:
      if self.left.type == PartialRegexNodeType.EMPTY_STRING:
        if self.right.type == PartialRegexNodeType.CONCATENATION:
          return f'({self.right})?'
        return f'{self.right}?'
      if self.right.type == PartialRegexNodeType.EMPTY_STRING:
        if self.left.type == PartialRegexNodeType.CONCATENATION:
          return f'({self.left})?'
        return f'{self.left}?'
      if self.left.type == PartialRegexNodeType.EMPTY_LANGUAGE:
        return str(self.right)
      if self.right.type == PartialRegexNodeType.EMPTY_LANGUAGE:
        return str(self.left)
      return f'({self.left}|{self.right})'
    if self.type == PartialRegexNodeType.HOLE:
      return str(PartialRegexNodeType.HOLE)
    if self.type == PartialRegexNodeType.STAR:
      a = self.left
      if a.type in (PartialRegexNodeType.EMPTY_STRING, PartialRegexNodeType.EMPTY_LANGUAGE):
        return str(a.type)
      if a.type == PartialRegexNodeType.STAR:
        return str(a)
      if a.type == PartialRegexNodeType.CONCATENATION:
        b, c = a.left, a.right
        if b.type == PartialRegexNodeType.STAR and c.type == PartialRegexNodeType.STAR:
          e, f = b.left, c.left
          # (e*f*)* -> (e|f)*
          return f'({e}|{f})*'
      if a.type == PartialRegexNodeType.LITERAL:
        return f'{a}*'
      return f'({a})*'
    if self.type == PartialRegexNodeType.OPTIONAL:
      a = self.left
      if a.type in (PartialRegexNodeType.CONCATENATION, PartialRegexNodeType.UNION):
        return f'({a})?'
      return f'{a}?'
    if self.type in (PartialRegexNodeType.EMPTY_STRING, PartialRegexNodeType.EMPTY_LANGUAGE):
      return str(self.type)
    return self.literal

  def get_cost(self) -> int:
    '''
    compute the complexity cost of the expression represented by this node (subtree)

    Returns:
        int: the cost
    '''
    c_literal = 1
    c_concatenation = 5
    c_star = 20
    c_optional = 20
    c_union = 30
    c_hole = 100
    match self.type:
      case PartialRegexNodeType.HOLE:
        return c_hole
      case PartialRegexNodeType.STAR:
        return self.left.cost() + c_star
      case PartialRegexNodeType.OPTIONAL:
        return self.left.cost() + c_optional
      case PartialRegexNodeType.CONCATENATION:
        return self.left.cost() + self.right.cost() + c_concatenation
      case PartialRegexNodeType.UNION:
        return self.left.cost() + self.right.cost() + c_union
    return c_literal

  def get_depth(self) -> int:
    '''
    compute the height of the node

    Returns:
        int: the height
    '''
    match self.type:
      case PartialRegexNodeType.HOLE:
        return 1
      case PartialRegexNodeType.STAR | PartialRegexNodeType.OPTIONAL:
        return self.left.get_depth() + 1
      case PartialRegexNodeType.CONCATENATION | PartialRegexNodeType.UNION:
        return max(self.left.get_depth(), self.right.get_depth()) + 1
    return 1

  def cost(self) -> int:
    '''
    the "cost" of this expression, a rough measure of complexity

    Returns:
        int: the cost
    '''
    if self._cost < 0:
      self._cost = self.get_cost() #+ int(10 ** (self.get_depth() - 2))
    return self._cost

  def copy(self) -> Self:
    '''
    make a deepcopy of this node (tree)

    Returns:
        Self: the copy
    '''
    s = PartialRegexNode(self.type, self.literal)
    if self.left:
      s.left = self.left.copy()
    if self.right:
      s.right = self.right.copy()
    return s

  def holes(self) -> int:
    '''
    the number of Holes in this node's expression

    Returns:
        int: the number of holes
    '''
    cnt = 0
    q = [self]
    while len(q) > 0:
      node = q.pop()
      if node.type == PartialRegexNodeType.HOLE:
        cnt += 1
      else:
        if node.right:
          q.append(node.right)
        if node.left:
          q.append(node.left)
    return cnt

  def fill(self, s: Self, index: int = 0) -> Self:
    '''
    fill a hole with the specifed expression

    Args:
        s (Self): expression to put in the hole
        index (int, optional): index of hole to fill. Defaults to 0.

    Raises:
        ValueError: no hole available to fill.

    Returns:
        Self: a copy of this node, but with the hole filled
    '''
    c = self.copy()
    q = [c]
    i = 0
    while len(q) > 0:
      node = q.pop()
      if node.type == PartialRegexNodeType.HOLE:
        if i == index:
          node.type = s.type
          node.left = s.left
          node.right = s.right
          node.literal = s.literal
          if c.holes() == 0:
            return opt(c)
          return c
        i += 1
      if node.right:
        q.append(node.right)
      if node.left:
        q.append(node.left)
    raise ValueError('no hole filled')

  def next_states(self, literals: str) -> list[Self]:
    '''
    the list of next states (nodes/expressions) from here

    Args:
        literals (str): the input alphabet

    Returns:
        list[Self]: the children of this node/expression
    '''
    states = []
    holes = self.holes()
    for hole in range(holes):
      for literal in literals + '.':
        states.append(self.fill(Literal(literal), hole))
      states.append(self.fill(EmptyString(), hole))
      states.append(self.fill(EmptyLanguage(), hole))
      states.append(self.fill(Concatenation(), hole))
      states.append(self.fill(Union(), hole))
      states.append(self.fill(Star(), hole))
    return states

  def overapproximation(self) -> Self:
    '''
    fill holes with .*

    Raises:
        ValueError: if type of node is unknown

    Returns:
        Self: a new node with holes filled with .*
    '''
    if self.type == PartialRegexNodeType.LITERAL:
      return Literal(self.literal)
    if self.type == PartialRegexNodeType.EMPTY_STRING:
      return EmptyString()
    if self.type == PartialRegexNodeType.EMPTY_LANGUAGE:
      return EmptyLanguage()
    if self.type == PartialRegexNodeType.UNION:
      return self.left.overapproximation() + self.right.overapproximation()
    if self.type == PartialRegexNodeType.CONCATENATION:
      return self.left.overapproximation() * self.right.overapproximation()
    if self.type == PartialRegexNodeType.STAR:
      return Star(self.left.overapproximation())
    if self.type == PartialRegexNodeType.OPTIONAL:
      return ZeroOrOne(self.left.overapproximation())
    if self.type == PartialRegexNodeType.HOLE:
      return Star(Literal('.'))
    raise ValueError(f'unknown type: {self.type}')

  def underapproximation(self) -> Self:
    '''
    fill holes with empty language

    Raises:
        ValueError: if type of node is unknown

    Returns:
        Self: a new node with holes filled with empty language
    '''
    if self.type == PartialRegexNodeType.LITERAL:
      return Literal(self.literal)
    if self.type == PartialRegexNodeType.EMPTY_STRING:
      return EmptyString()
    if self.type == PartialRegexNodeType.EMPTY_LANGUAGE:
      return EmptyLanguage()
    if self.type == PartialRegexNodeType.UNION:
      return self.left.underapproximation() + self.right.underapproximation()
    if self.type == PartialRegexNodeType.CONCATENATION:
      return self.left.underapproximation() * self.right.underapproximation()
    if self.type == PartialRegexNodeType.STAR:
      return Star(self.left.underapproximation())
    if self.type == PartialRegexNodeType.OPTIONAL:
      return ZeroOrOne(self.left.underapproximation())
    if self.type == PartialRegexNodeType.HOLE:
      return EmptyLanguage()
    raise ValueError(f'unknown type: {self.type}')

  def unroll(self) -> Self:
    '''
    pull two instances of e out of every e*

    Raises:
        ValueError: if type of node is unknown

    Returns:
        Self: a new node where each e* is replaced by eee*
    '''
    if self.type == PartialRegexNodeType.LITERAL:
      return Literal(self.literal)
    if self.type == PartialRegexNodeType.EMPTY_STRING:
      return EmptyString()
    if self.type == PartialRegexNodeType.EMPTY_LANGUAGE:
      return EmptyLanguage()
    if self.type == PartialRegexNodeType.UNION:
      return self.left.unroll() + self.right.unroll()
    if self.type == PartialRegexNodeType.CONCATENATION:
      return self.left.unroll() * self.right.unroll()
    if self.type == PartialRegexNodeType.STAR:
      e = self.left.copy()
      return e * e * Star(e)
    if self.type == PartialRegexNodeType.HOLE:
      return Hole()
    raise ValueError(f'unknown type: {self.type}')

  def split(self) -> set[Self]:
    '''
    a set of expressions resulting from splitting at every concatenation

    Raises:
        ValueError: if type of node is unknown

    Returns:
        set[Self]: new nodes resulting from splitting each concatenation
    '''
    if self.type == PartialRegexNodeType.LITERAL:
      return {Literal(self.literal)}
    if self.type == PartialRegexNodeType.EMPTY_STRING:
      return {EmptyString()}
    if self.type == PartialRegexNodeType.EMPTY_LANGUAGE:
      return {EmptyLanguage()}
    if self.type == PartialRegexNodeType.UNION:
      return self.left.split().union(self.right.split())
    if self.type == PartialRegexNodeType.CONCATENATION:
      s = set()
      for e in self.left.split():
        c = PartialRegexNode(PartialRegexNodeType.CONCATENATION)
        c.left = e
        c.right = self.right.copy()
        s.add(c)
      for e in self.right.split():
        c = PartialRegexNode(PartialRegexNodeType.CONCATENATION)
        c.left = self.left.copy()
        c.right = e
        s.add(c)
      return s
    if self.type == PartialRegexNodeType.STAR:
      return {self.copy()}
    if self.type == PartialRegexNodeType.HOLE:
      return {Hole()}
    raise ValueError(f'unknown type: {self.type}')

  def is_dead(self, P: set[str], N: set[str]) -> bool:
    '''
    determine if this state is dead (not possibly an ancestor of a solution)

    Args:
        P (set[str]): positive examples
        N (set[str]): negatvie examples

    Returns:
        bool: True iff this state is dead (cannot lead to a solution)
    '''
    # check for deadness
    o = self.overapproximation()
    s = opt(opt(o))
    overapproximation = str(s)
    if not matches_all(overapproximation, P):
      # dead
      return True

    u = self.underapproximation()
    s = opt(opt(u))
    underapproximation = str(s)
    if matches_any(underapproximation, N):
      # dead
      return True

    # redundant states
    A = self.unroll().split()
    for e in A:
      overapproximation = opt(opt(e.overapproximation()))
      if not matches_any(str(overapproximation), P):
        # dead
        return True
    return False

  def is_solution(self, P: set[str], N: set[str]) -> bool:
    '''
    determines whether this state is a solution (matches all positive and no negetvie examples)

    Args:
        P (set[str]): positive examples
        N (set[str]): negative examples

    Returns:
        bool: True iff the regex this state represents matches all positive and no negative examples
    '''
    if self.holes() > 0:
      return False
    pattern = str(opt(self))
    return matches_all(pattern, P) and not matches_any(pattern, N)

def Literal(symbol: str) -> PartialRegexNode:
  '''
  create a Literal node

  Args:
      symbol (str): symbol at this node

  Raises:
      ValueError: if length of symbol is not 1

  Returns:
      PartialRegexNode: a literal node
  '''
  if len(symbol) != 1:
    raise ValueError('length of literal must be exactly 1')
  return PartialRegexNode(PartialRegexNodeType.LITERAL, symbol)

def EmptyString() -> PartialRegexNode:
  '''
  create an empty string node

  Returns:
      PartialRegexNode: an empty string node
  '''
  return PartialRegexNode(PartialRegexNodeType.EMPTY_STRING)

def EmptyLanguage() -> PartialRegexNode:
  '''
  create an empty language node

  Returns:
      PartialRegexNode: an empty language node
  '''
  return PartialRegexNode(PartialRegexNodeType.EMPTY_LANGUAGE)

def Hole() -> PartialRegexNode:
  '''
  create a hole node

  Returns:
      PartialRegexNode: a hole node
  '''
  return PartialRegexNode(PartialRegexNodeType.HOLE)

def Concatenation(s1: PartialRegexNode = Hole(), s2: PartialRegexNode = Hole()) -> PartialRegexNode:
  '''
  create a concatenation node

  Args:
      s1 (PartialRegexNode, optional): left expression. Defaults to Hole().
      s2 (PartialRegexNode, optional): right expression. Defaults to Hole().

  Returns:
      PartialRegexNode: s1 concatenated with s2 (s1s2)
  '''
  return s1 * s2

def Union(s1: PartialRegexNode = Hole(), s2: PartialRegexNode = Hole()) -> PartialRegexNode:
  '''
  create a union node

  Args:
      s1 (PartialRegexNode, optional): left expression. Defaults to Hole().
      s2 (PartialRegexNode, optional): right expression. Defaults to Hole().

  Returns:
      PartialRegexNode: union of s1 and s2 (s1|s2)
  '''
  return s1 + s2

def Star(s: PartialRegexNode = Hole()) -> PartialRegexNode:
  '''
  create a kleene star node

  Args:
      s (PartialRegexNode, optional): the expression to be starred. Defaults to Hole().

  Returns:
      PartialRegexNode: the kleene star of s (s*)
  '''
  s1 = PartialRegexNode(PartialRegexNodeType.STAR)
  s1.left = s.copy()
  return s1

def ZeroOrOne(s: PartialRegexNode = Hole()) -> PartialRegexNode:
  '''
  create an optional node

  Args:
      s (PartialRegexNode, optional): expression to optionalize. Defaults to Hole().

  Returns:
      PartialRegexNode: the option of s (s?)
  '''
  s1 = PartialRegexNode(PartialRegexNodeType.OPTIONAL)
  s1.left = s.copy()
  return s1

def opt(s: PartialRegexNode) -> PartialRegexNode:
  '''
  simplify a regex

  Args:
    s (PartialRegexNode): regex to simplify

  Returns:
    PartialRegexNode: possibly simplifed regex
  '''
  match s.type:
    case PartialRegexNodeType.CONCATENATION:
      return opt_concatentation(s)

    case PartialRegexNodeType.UNION:
      return opt_union(s)

    case PartialRegexNodeType.STAR:
      return opt_star(s)

    case PartialRegexNodeType.OPTIONAL:
      return opt_optional(s)
  # literals, empties, holes
  return s

def opt_concatentation(s: PartialRegexNode) -> PartialRegexNode:
  '''
  simplify a concatenation

  Args:
     s (PartialRegexNode): regex to simplify

  Returns:
    PartialRegexNode: possibly simplifed regex
  '''
  if s.type != PartialRegexNodeType.CONCATENATION:
    return s
  # e1e2
  e1 = opt(s.left)
  e2 = opt(s.right)
  if e1.type == PartialRegexNodeType.EMPTY_LANGUAGE or e2.type == PartialRegexNodeType.EMPTY_LANGUAGE:
    # ∅e2 = e1∅ -> ∅
    return EmptyLanguage()
  if e1.type == PartialRegexNodeType.EMPTY_STRING:
    # εe2 -> e2
    return e2
  if e2.type == PartialRegexNodeType.EMPTY_STRING:
    # e1ε -> e1
    return e1
  if e1.type == PartialRegexNodeType.STAR and e2.type == PartialRegexNodeType.STAR and e1.left == e2.left:
    # e*e* -> e*
    return Star(e1.left)
  if e1.type == PartialRegexNodeType.STAR and e2.type == PartialRegexNodeType.OPTIONAL and e1.left == e2.left:
    # e*e? -> e*
    return Star(e1.left)
  if e1.type == PartialRegexNodeType.OPTIONAL and e2.type == PartialRegexNodeType.STAR and e1.left == e2.left:
    # e?e* -> e*
    return Star(e1.left)
  if e1.type == PartialRegexNodeType.CONCATENATION:
    f1 = e1.left
    f2 = e1.right
    # (f1f2)e2
    if f2.type == PartialRegexNodeType.STAR and e2.type == PartialRegexNodeType.STAR and f2.left == e2.left:
      # (f1e*)e* ->f1e*
      return Concatenation(f1, Star(e2.left))
    if f2.type == PartialRegexNodeType.OPTIONAL and e2.type == PartialRegexNodeType.STAR and f2.left == e2.left:
      # (f1e?)e* ->f1e*
      return Concatenation(f1, Star(e2.left))
    if f2.type == PartialRegexNodeType.STAR and e2.type == PartialRegexNodeType.OPTIONAL and f2.left == e2.left:
      # (f1e*)e? ->f1e*
      return Concatenation(f1, Star(e2.left))
  if e2.type == PartialRegexNodeType.CONCATENATION:
    f1 = e2.left
    f2 = e2.right
    # e1(f1f2)
    if e1.type == PartialRegexNodeType.STAR and f1.type == PartialRegexNodeType.STAR and e1.left == f1.left:
      # e*(e*f2) ->e*f2
      return Concatenation(Star(e1.left), f2)
    if e1.type == PartialRegexNodeType.OPTIONAL and f1.type == PartialRegexNodeType.STAR and e1.left == f1.left:
      # e?(e*f2) ->e*f2
      return Concatenation(Star(e1.left), f2)
    if e1.type == PartialRegexNodeType.STAR and f1.type == PartialRegexNodeType.OPTIONAL and e1.left == f1.left:
      # e*(e?f2) ->e*f2
      return Concatenation(Star(e1.left), f2)
  return Concatenation(e1, e2)

def opt_union(s: PartialRegexNode) -> PartialRegexNode:
  '''
  simplify a union

  Args:
    s (PartialRegexNode): regex to simplify

  Returns:
    PartialRegexNode: possibly simplifed regex
  '''
  if s.type != PartialRegexNodeType.UNION:
    return s
  # e1|e2
  e1 = opt(s.left)
  e2 = opt(s.right)
  if e1.type == PartialRegexNodeType.EMPTY_LANGUAGE:
    # ∅|e2
    return e2
  if e2.type == PartialRegexNodeType.EMPTY_LANGUAGE:
    # e1|∅
    return e1
  if e1.type == PartialRegexNodeType.EMPTY_STRING:
    # ε|e2 -> e2?
    return ZeroOrOne(e2)
  if e2.type == PartialRegexNodeType.EMPTY_STRING:
    # e1|ε -> e1?
    return ZeroOrOne(e1)
  if e1 == e2:
    # e|e -> e
    return e1
  if e2.type == PartialRegexNodeType.STAR:
    # e1|e2*
    if e1 == e2.left:
      # e|e* -> e*
      return Star(e1)
    if e1.type == PartialRegexNodeType.UNION:
      # (f1|f2)|e2*
      f1 = e1.left
      f2 = e1.right
      if f1 == e2.left:
        # (e2|f2)e2* -> f2|e2*
        return Union(f2, Star(e2.left))
      if f2 == e2.left:
        # (f1|e2)e2* -> f1|e2*
        return Union(f1, Star(e2.left))
  if e2.type == PartialRegexNodeType.OPTIONAL:
    # e1|e2?
    if e1 == e2.left:
      # e|e? -> e?
      return ZeroOrOne(e1)
    if e1.type == PartialRegexNodeType.UNION:
      # (f1|f2)|e2?
      f1 = e1.left
      f2 = e1.right
      if f1 == e2.left:
        # (e2|f2)|e2? -> f2|e2?
        return Union(f2, ZeroOrOne(e2.left))
      if f2 == e2.left:
        # (f1|e2)|e2? -> f1|e2?
        return Union(f1, ZeroOrOne(e2.left))
  if e1.type == PartialRegexNodeType.STAR:
    # e1*|e2
    if e1.left == e2:
      # e*|e -> e*
      return Star(e2)
    if e2.type == PartialRegexNodeType.UNION:
      # e1*|(f1|f2)
      f1 = e2.left
      f2 = e2.right
      if e1.left == f1:
        # e1*|(e1|f2) -> e1*|f2
        return Union(Star(e1.left), f2)
      if e1.left == f2:
        # e1*|(f1|e1) -> e1*|f1
        return Union(Star(e1.left), f1)
  if e1.type == PartialRegexNodeType.OPTIONAL:
    # e1?|e2
    if e1.left == e2:
      # e?|e -> e?
      return ZeroOrOne(e2)
    if e2.type == PartialRegexNodeType.UNION:
      # e1?|(f1|f2)
      f1 = e2.left
      f2 = e2.right
      if e1.left == f1:
        # e1?|(e1|f2) -> e1?|f2
        return Union(ZeroOrOne(e1.left), f2)
      if e1.left == f2:
        # e1?|(f1|e1) -> e1?|f1
        return Union(ZeroOrOne(e1.left), f1)
  if e1.type == PartialRegexNodeType.UNION:
    # (f1|f2)|e2
    f1 = e1.left
    f2 = e1.right
    if f2.type == PartialRegexNodeType.STAR and f2.left == e2:
      # (f1|e2*)|e2 -> f1|e2*
      return Union(f1, Star(e2))
    if f1.type == PartialRegexNodeType.STAR and f1.left == e2:
      # (e2*|f2)|e2 -> e2*|f2
      return Union(Star(e2), f2)
    if f2.type == PartialRegexNodeType.OPTIONAL and f2.left == e2:
      # (f1|e2?)|e2 -> f1|e2?
      return Union(f1, ZeroOrOne(e2))
    if f1.type == PartialRegexNodeType.OPTIONAL and f1.left == e2:
      # (e2?|f2)|e2 -> e2?|f2
      return Union(ZeroOrOne(e2), f2)
    if e2 == f1:
      # (e2|f2)|e2 -> e2|f2
      return Union(e2, f2)
    if e2 == f2:
      # (f1|e2)|e2 -> f1|e2
      return Union(f1, e2)
  if e2.type == PartialRegexNodeType.UNION:
    # e1|(f1|f2)
    f1 = e2.left
    f2 = e2.right
    if f2.type == PartialRegexNodeType.STAR and f2.left == e1:
      # e1|(f1|e1*) -> f1|e1*
      return Union(f1, Star(e1))
    if f1.type == PartialRegexNodeType.STAR and f1.left == e1:
      # e1|(e1*|f2) -> e1*|f2
      return Union(Star(e1), f2)
    if f2.type == PartialRegexNodeType.OPTIONAL and f2.left == e1:
      # e1|(f1|e1?) -> f1|e1?
      return Union(f1, ZeroOrOne(e1))
    if f1.type == PartialRegexNodeType.OPTIONAL and f1.left == e1:
      # e1|(e1?|f2) -> e1?|f2
      return Union(ZeroOrOne(e1), f2)
    if e1 == f1:
      # e1|(e1|f2) -> e1|f2
      return Union(e1, f2)
    if e1 == f2:
      # e1|(f1|e1) -> e1|f1
      return Union(e1, f1)
  return Union(e1, e2)

def opt_star(s: PartialRegexNode) -> PartialRegexNode:
  '''
  simplify a kleene star

  Args:
    s (PartialRegexNode): regex to simplify

  Returns:
    PartialRegexNode: possibly simplifed regex
  '''
  if s.type != PartialRegexNodeType.STAR:
    return s
  # e*
  e = opt(s.left)
  if e.type == PartialRegexNodeType.EMPTY_LANGUAGE:
    # ∅* -> ∅
    return EmptyLanguage()
  if e.type == PartialRegexNodeType.EMPTY_STRING:
    # ε* -> ε
    return EmptyString()
  if e.type == PartialRegexNodeType.STAR:
    # e** -> e*
    return Star(e.left)
  if e.type == PartialRegexNodeType.OPTIONAL:
    # e?* -> e*
    return Star(e.left)
  if e.type == PartialRegexNodeType.CONCATENATION:
    # (e1e2)*
    e1 = e.left
    e2 = e.right
    if e2.type == PartialRegexNodeType.STAR and e1 == e2.left:
      # (ee*)* -> e*
      return Star(e1)
    if e1.type == PartialRegexNodeType.STAR and e1.left == e2:
      # (e*e)* -> e*
      return Star(e2)
    if e1.type == PartialRegexNodeType.STAR and e2.type == PartialRegexNodeType.STAR:
      # (e*f*)* -> (e|f)*
      return Star(Union(e1.left, e2.left))
    if e1.type == PartialRegexNodeType.OPTIONAL and e2.type == PartialRegexNodeType.OPTIONAL:
      # (e?f?)* -> (e|f)*
      return Star(Union(e1.left, e2.left))
    if e1.type == PartialRegexNodeType.OPTIONAL and e1.left == e2:
      # (e?e)* -> e*
      return Star(e2)
    if e2.type == PartialRegexNodeType.OPTIONAL and e2.left == e1:
      # (ee?)* -> e*
      return Star(e1)
  return Star(e)

def opt_optional(s: PartialRegexNode) -> PartialRegexNode:
  '''
  simplify a zero or one

  Args:
    s (PartialRegexNode): regex to simplify

  Returns:
    PartialRegexNode: possibly simplifed regex
  '''
  if s.type != PartialRegexNodeType.OPTIONAL:
    return s
  # e?
  e = opt(s.left)
  if e.type == PartialRegexNodeType.EMPTY_LANGUAGE:
    # ∅? -> ε
    return EmptyString()
  if e.type == PartialRegexNodeType.EMPTY_STRING:
    # ε? -> ε
    return EmptyString()
  if e.type == PartialRegexNodeType.STAR:
    # f*? -> f*
    f = e.left
    return Star(f)
  if e.type == PartialRegexNodeType.OPTIONAL:
    # f?? -> f?
    f = e.left
    return ZeroOrOne(f)
  if e.type == PartialRegexNodeType.CONCATENATION:
    # (e1e2)?
    e1 = e.left
    e2 = e.right
    if e1.type == PartialRegexNodeType.STAR and e1.left == e2:
      # (e*e)? -> e*
      return Star(e2)
    if e2.type == PartialRegexNodeType.STAR and e2.left == e1:
      # (ee*)? -> e*
      return Star(e1)
    if e1.type == PartialRegexNodeType.STAR and e2.type == PartialRegexNodeType.STAR:
      # (e*f*)? -> e*f*
      return Concatenation(e1, e2)
    if e1.type == PartialRegexNodeType.OPTIONAL and e2.type == PartialRegexNodeType.OPTIONAL:
      # (e?f?)? -> e?f?
      return Concatenation(e1, e2)
  return ZeroOrOne(e)
