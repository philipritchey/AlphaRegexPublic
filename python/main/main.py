import heapq
import re
from main.partial_regex import PartialRegexNode, Hole
from typing import Set, List

def matches_all(pattern: str, examples: Set[str]) -> bool:
    for example in examples:
        if not re.fullmatch(pattern, example):
            return False
    return True

def matches_any(pattern: str, examples: Set[str]) -> bool:
    for example in examples:
        if re.fullmatch(pattern, example):
            return True
    return False

def get_literals(examples: Set[str]) -> str:
    literals = '.'
    for example in examples:
        for symbol in example:
            if symbol not in literals:
                literals += symbol
    return literals

def solution(state: PartialRegexNode, P: Set[str], N: Set[str]) -> bool:
    pattern = str(state)
    return state.holes() == 0 and matches_all(pattern, P) and not matches_any(pattern, N)

def dead(state: PartialRegexNode, P: Set[str], N: Set[str]) -> bool:
    # check for deadness
    overapproximation = str(state.overapproximation())
    if not matches_all(overapproximation, P):
        # dead
        return True
    
    underapproximation = str(state.underapproximation())
    if matches_any(underapproximation, N):
        # dead
        return True
    
    # redundant states
    A = state.unroll().split()
    for e in A:
        overapproximation = e.overapproximation()
        if not matches_any(str(overapproximation), P):
            # dead
            return True
    return False

def search(P: Set[str], N: Set[str]) -> str:
    literals = get_literals(P)
    initial = Hole()
    q: List[PartialRegexNode] = []
    heapq.heappush(q, initial)
    v_pre = set()
    v_post = set()
    while True:
        state = heapq.heappop(q)
        if state in v_post:
            continue
        v_post.add(state)
        if solution(state, P, N):
            return str(state)
        else:
            if dead(state, P, N):
                continue
            # if not dead, expand and add to queue
            for next_state in state.next_states(literals):
                if next_state not in v_pre:
                    heapq.heappush(q, next_state)
                    v_pre.add(next_state)

