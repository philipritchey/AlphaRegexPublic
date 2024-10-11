import heapq
import re
import sys
from time import time
from main.partial_regex import PartialRegexNode, Hole

def matches_all(pattern: str, examples: set[str]) -> bool:
    for example in examples:
        if not re.fullmatch(pattern, example):
            return False
    return True

def matches_any(pattern: str, examples: set[str]) -> bool:
    for example in examples:
        if re.fullmatch(pattern, example):
            return True
    return False

def get_literals(examples: set[str]) -> str:
    literals = '.'
    for example in examples:
        for symbol in example:
            if symbol not in literals:
                literals += symbol
    return literals

def solution(state: PartialRegexNode, P: set[str], N: set[str]) -> bool:
    pattern = str(state)
    return state.holes() == 0 and matches_all(pattern, P) and not matches_any(pattern, N)

def dead(state: PartialRegexNode, P: set[str], N: set[str]) -> bool:
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

def search(P: set[str], N: set[str]) -> str:
    literals = get_literals(P)
    initial = Hole()
    q: list[PartialRegexNode] = []
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


def main(examples: str) -> str:
    P: set[str] = set()
    N: set[str] = set()
    with open(examples, 'r') as f:
        description = f.readline().strip()
        active_set = P
        for line in f:
            line = line.strip()
            if line == '++':
                active_set = P
            elif line == '--':
                active_set = N
            else:
                active_set.add(line)
    print(description)
    t1 = time()
    solution = search(P, N)
    t2 = time()
    print(solution.replace('X', '.'))
    dt = t2 - t1
    units = 's'
    if dt < 1:
        dt *= 1000
        units = 'ms'
    print(f'{dt:0.2f} {units}')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('error: missing required examples filename')
        sys.exit(1)
    examples = sys.argv[1]
    print(f'{examples=}')
    main(examples)
