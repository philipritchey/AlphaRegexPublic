from enum import StrEnum
from functools import total_ordering
from typing import Self, Optional, List, Set

class PartialRegexNodeType(StrEnum):
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
    def __init__(self, type: Optional[PartialRegexNodeType] = PartialRegexNodeType.HOLE, literal: Optional[str] = None):
        self.type = type
        self.left: Self = None
        self.right: Self = None
        self.literal: Optional[str] = None
        if type == PartialRegexNodeType.LITERAL:
            if len(literal) != 1:
                raise ValueError('length of literal must be exactly 1')
            self.literal = literal

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
                if self.right.type in (PartialRegexNodeType.CONCATENATION, PartialRegexNodeType.UNION):
                    return f'({self.right})?'
                return f'{self.right}?'
            if self.right.type == PartialRegexNodeType.EMPTY_STRING:
                if self.left.type in (PartialRegexNodeType.CONCATENATION, PartialRegexNodeType.UNION):
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
        if self.type in (PartialRegexNodeType.EMPTY_STRING, PartialRegexNodeType.EMPTY_LANGUAGE):
            return str(self.type)
        return self.literal

    def cost(self) -> int:
        c_literal = 1
        c_concatenation = 2
        c_star = 3
        c_union = 20
        c_hole = 100
        if self.type == PartialRegexNodeType.HOLE:
            return c_hole
        if self.type == PartialRegexNodeType.STAR:
            return self.left.cost() + c_star
        if self.type == PartialRegexNodeType.CONCATENATION:
            return self.left.cost() + self.right.cost() + c_concatenation
        if self.type == PartialRegexNodeType.UNION:
            return self.left.cost() + self.right.cost() + c_union
        return c_literal

    def copy(self) -> Self:
        s = PartialRegexNode(self.type, self.literal)
        if self.left:
            s.left = self.left.copy()
        if self.right:
            s.right = self.right.copy()
        return s

    def holes(self) -> int:
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
                    return c
                i += 1
            if node.right:
                q.append(node.right)
            if node.left:
                q.append(node.left)
        raise ValueError('no hole filled')

    def next_states(self, literals: str) -> List[Self]:
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
        if self.type == PartialRegexNodeType.HOLE:
            return Star(Literal('.'))
        raise ValueError(f'unknown type: {self.type}')

    def underapproximation(self) -> Self:
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
        if self.type == PartialRegexNodeType.HOLE:
            return EmptyLanguage()
        raise ValueError(f'unknown type: {self.type}')

    def unroll(self) -> Self:
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

    def split(self) -> Set[Self]:
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

def Literal(symbol: str) -> PartialRegexNode:
    if len(symbol) != 1:
        raise ValueError('length of literal must be exactly 1')
    return PartialRegexNode(PartialRegexNodeType.LITERAL, symbol)

def EmptyString() -> PartialRegexNode:
    return PartialRegexNode(PartialRegexNodeType.EMPTY_STRING)

def EmptyLanguage() -> PartialRegexNode:
    return PartialRegexNode(PartialRegexNodeType.EMPTY_LANGUAGE)

def Hole() -> PartialRegexNode:
    return PartialRegexNode(PartialRegexNodeType.HOLE)

def Concatenation(s1: PartialRegexNode = Hole(), s2: PartialRegexNode = Hole()) -> PartialRegexNode:
    return s1 * s2

def Union(s1: PartialRegexNode = Hole(), s2: PartialRegexNode = Hole()) -> PartialRegexNode:
    return s1 + s2

def Star(s: PartialRegexNode = Hole()) -> PartialRegexNode:
    s1 = PartialRegexNode(PartialRegexNodeType.STAR)
    s1.left = s.copy()
    return s1

def opt(s: PartialRegexNode) -> PartialRegexNode:
    match s.type:
        case PartialRegexNodeType.CONCATENATION:
            # e1e2
            e1 = s.left
            e2 = s.right
            if e1.type == PartialRegexNodeType.STAR and e2.type == PartialRegexNodeType.STAR and e1.left == e2.left:
                # e*e* -> e*
                return Star(opt(e1))
            if e1.type == PartialRegexNodeType.CONCATENATION:
                f1 = e1.left
                f2 = e1.right
                # (f1f2)e2
                if f2.type == PartialRegexNodeType.STAR and e2.type == PartialRegexNodeType.STAR and f2.left == e2.left:
                    # (f1e*)e* ->f1e*
                    return Concatenation(f1, Star(opt(e2.left)))
            if e2.type == PartialRegexNodeType.CONCATENATION:
                f1 = e2.left
                f2 = e2.right
                # e1(f1f2)
                if e1.type == PartialRegexNodeType.STAR and f1.type == PartialRegexNodeType.STAR and e1.left == f1.left:
                    # e*(e*f2) ->e*f2
                    return Concatenation(Star(opt(e1.left)), f2)
            return Concatenation(opt(e1), opt(e2))

        case PartialRegexNodeType.UNION:
            # e1|e2
            e1 = s.left
            e2 = s.right
            if e1 == e2:
                # e|e -> e
                return opt(e1)
            if e2.type == PartialRegexNodeType.STAR:
                # e1|e2*
                if e1 == e2.left:
                    # e|e* -> e*
                    return Star(opt(e1))
                if e1.type == PartialRegexNodeType.UNION:
                    # (f1|f2)|e2*
                    f1 = e1.left
                    f2 = e1.right
                    if f1 == e2.left:
                        # (e2|f2)e2* -> f2|e2*
                        return Union(opt(f2), Star(opt(e2.left)))
                    if f2 == e2.left:
                        # (f1|e2)e2* -> f1|e2*
                        return Union(opt(f1), Star(opt(e2.left)))
            if e1.type == PartialRegexNodeType.STAR:
                # e1*|e2
                if e1.left == e2:
                    # e*|e -> e*
                    return Star(opt(e2))
                if e2.type == PartialRegexNodeType.UNION:
                    # e1*|(f1|f2)
                    f1 = e2.left
                    f2 = e2.right
                    if e1.left == f1:
                        # e1*|(e1|f2) -> e1*|f2
                        return Union(Star(opt(e1.left)), opt(f2))
                    if e1.left == f2:
                        # e1*|(f1|e1) -> e1*|f1
                        return Union(Star(opt(e1.left)), opt(f1))
            if e1.type == PartialRegexNodeType.UNION:
                # (f1|f2)|e2
                f1 = e1.left
                f2 = e1.right
                if f2.type == PartialRegexNodeType.STAR and f2.left == e2:
                    # (f1|e2*)|e2 -> f1|e2*
                    return Union(opt(f1), Star(opt(e2)))
                if f1.type == PartialRegexNodeType.STAR and f1.left == e2:
                    # (e2*|f2)|e2 -> e2*|f2
                    return Union(Star(opt(e2)), opt(f2))
                if e2 == f1:
                    # (e2|f2)|e2 -> e2|f2
                    return Union(opt(e2), opt(f2))
                if e2 == f2:
                    # (f1|e2)|e2 -> f1|e2
                    return Union(opt(f1), opt(e2))
            if e2.type == PartialRegexNodeType.UNION:
                # e1|(f1|f2)
                f1 = e2.left
                f2 = e2.right
                if f2.type == PartialRegexNodeType.STAR and f2.left == e1:
                    # e1|(f1|e1*) -> f1|e1*
                    return Union(opt(f1), Star(opt(e1)))
                if f1.type == PartialRegexNodeType.STAR and f1.left == e1:
                    # e1|(e1*|f2) -> e1*|f2
                    return Union(Star(opt(e1)), opt(f2))
                if e1 == f1:
                    # e1|(e1|f2) -> e1|f2
                    return Union(opt(e1), opt(f2))
                if e1 == f2:
                    # e1|(f1|e1) -> e1|f1
                    return Union(opt(e1), opt(f1))
            return Union(opt(e1), opt(e2))

        case PartialRegexNodeType.STAR:
            # e*
            e = s.left
            if e.type == PartialRegexNodeType.STAR:
                # e** -> e*
                return Star(opt(e.left))
            if e.type == PartialRegexNodeType.CONCATENATION:
                # (e1e2)*
                e1 = e.left
                e2 = e.right
                if e2.type == PartialRegexNodeType.STAR and e1 == e2.left:
                    # ee* -> e*
                    return Star(opt(e1))
                if e1.type == PartialRegexNodeType.STAR and e1.left == e2:
                    # e*e -> e*
                    return Star(opt(e2))
            return Star(opt(e))
    return s