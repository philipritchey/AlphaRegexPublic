import heapq
import re
from main.partial_regex import PartialRegexNode, Hole
from main.main import get_literals, matches_all, matches_any, solution
from typing import Set, List

def dead(state: PartialRegexNode, P: Set[str], N: Set[str]) -> bool:
    # check for deadness
    overapproximation = str(state.overapproximation())
    print(f'  over={overapproximation}')
    if not matches_all(overapproximation, P):
        # dead
        return True
    
    underapproximation = str(state.underapproximation())
    print(f'  under={underapproximation}')
    if matches_any(underapproximation, N):
        # dead
        return True
    
    # redundant states
    A = state.unroll().split()
    for e in A:
        overapproximation = e.overapproximation()
        print(f'  e^={overapproximation}')
        if not matches_any(str(overapproximation), P):
            # dead
            return True
    return False

def search(P: Set[str], N: Set[str], **kwargs) -> str:
    '''
    find a regex that matches all p in P and not any n in N

    Args
        P: set of positive examples
        N: set of negative examples
        keywords
            pause - pause after every step
            verbose - print more info
            initial - inital expression from which to search
            
    '''
    pause = kwargs['pause'] if 'pause' in kwargs else True
    verbose = kwargs['verbose'] if 'verbose' in kwargs else True
    initial = kwargs['initial'] if 'initial' in kwargs else Hole()

    literals = get_literals(P)
    print(f'{literals=}')
    initial = Hole()
    q: List[PartialRegexNode] = []
    heapq.heappush(q, initial)
    v_pre = set()
    v_post = set()
    while True:
        input('Press enter to continue...')
        print(f'|q|= {len(q)}')
        state = heapq.heappop(q)
        if state in v_post:
            continue
        v_post.add(state)
        print(f'state={state}, {state.cost()}')
        if solution(state, P, N):
            return str(state)
        else:
            if dead(state, P, N):
                print('  is DEAD')
                continue
            # if not dead, expand and add to queue
            print('  is ALIVE')
            print('  next states:')
            for next_state in state.next_states(literals):
                print(f'    {next_state}', end='')
                if next_state not in v_pre:
                    heapq.heappush(q, next_state)
                    v_pre.add(next_state)
                    print(' (new)')
                else:
                    print()



def interactive_search(P: Set[str], N: Set[str], **kwargs) -> str:
    pause = kwargs['pause'] if 'pause' in kwargs else True
    verbose = kwargs['verbose'] if 'verbose' in kwargs else True
    initial = kwargs['initial'] if 'initial' in kwargs else Hole()
    literals = get_literals(P)
    print(f'{literals=}')
    q: List[PartialRegexNode] = []
    heapq.heappush(q, initial)
    v_pre = set()
    v_post = set()
    steps = 0
    while True:
        if pause:
            input('Press enter to continue...')
        steps += 1
        print(f'{steps=}')
        print(f'|q|= {len(q)}')
        state = heapq.heappop(q)
        if state in v_post:
            continue
        v_post.add(state)
        print(f'state={state}, {state.cost()}')
        if state.holes() == 0:
            # check for solution
            pattern = str(state)
            if verbose:
                print(f'  checking /{pattern}/')
            if matches_all(pattern, P) and not matches_any(pattern, N):
                if verbose:
                    print(f'  PASS')
                return pattern
            if verbose:
                print('  FAIL')
        else:
            # check for deadness
            overapproximation = str(state.overapproximation())
            if verbose:
                print(f'  over={overapproximation}', end='')
            if not matches_all(overapproximation, P):
                # dead
                if verbose:
                    print(' is DEAD: does not match all positive examples')
                continue
            if verbose:
                print(' is ALIVE: matches all positive examples')
            underapproximation = str(state.underapproximation())
            if verbose:
                print(f'  under={underapproximation}', end='')
            if matches_any(underapproximation, N):
                # dead
                if verbose:
                    print(' is DEAD: matches some negative example')
                continue
            if verbose:
                print(' is ALIVE: does not match any negative example')
            # redundant states
            A = state.unroll().split()
            dead = False
            for e in A:
                overapproximation = e.overapproximation()
                if verbose:
                    print(f'  e^={overapproximation}', end='')
                if not matches_any(str(overapproximation), P):
                    # dead
                    if verbose:
                        print(' is DEAD: does not match any positive example')
                    dead = True
                    break
                if verbose:
                    print(' is ALIVE: matches some positive example')
            if dead:
                continue
            # if not dead, expand and add to queue
            if verbose:
                print('  next states:')
            for next_state in state.next_states(literals):
                if verbose:
                    print(f'    {next_state}, {next_state.cost()}', end='')
                if next_state not in v_pre:
                    heapq.heappush(q, next_state)
                    v_pre.add(next_state)
                    if verbose:
                        print(' (new)')
                elif verbose:
                    print()

if __name__ == '__main__':
    P = {}
    N = {}
    pattern = interactive_search(P, N)
    # P = {'0101', '00101', '01010', '10101', '01011', '1101111001000101100111000'}
    # N = {'0', '1', '00', '01', '10', '11', '000', '001', '010', '011', '100', '101', '110', '111','0000', '0001', '0010', '0011', '0100', '0110', '0111', '1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111'}
    # 6300 steps (but not always?)
    # pattern = interactive_search(P, N, pause=False, verbose=False)
    # 10119 steps
    # pattern = interactive_search(P, N, initial=Hole()*Hole(), pause=False, verbose=False)
    # 5925 steps 
    # pattern = interactive_search(P, N, initial=Star()*Hole(), pause=False, verbose=False)
    # 5249 steps
    # pattern = interactive_search(P, N, initial=Hole()*Star(), pause=False, verbose=False)
    # 5148 steps
    # pattern = interactive_search(P, N, initial=Hole()*Hole()*Hole(), pause=False, verbose=False)
    # 3476 steps
    # pattern = interactive_search(P, N, initial=Hole()*Hole()*Star(), pause=False, verbose=False)
    # 1548 steps
    # pattern = interactive_search(P, N, initial=Star()*Hole()*Hole(), pause=False, verbose=False)
    # 1459 steps
    # pattern = interactive_search(P, N, initial=Star()*Hole()*Star(), pause=False, verbose=False)
    # 312 steps
    # pattern = interactive_search(P, N, initial=Hole()*Literal('0')*Literal('1')*Hole()*Hole()*Hole(), pause=False, verbose=False)
    # 92 steps
    # pattern = interactive_search(P, N, initial=Star()*Literal('0')*Hole()*Literal('0')*Hole()*Star(), pause=False, verbose=False)
    # 83 steps
    # pattern = interactive_search(P, N, initial=Hole()*Literal('0')*Literal('1')*Literal('0')*Hole()*Hole(), pause=False, verbose=False)
    # 29 steps
    # pattern = interactive_search(P, N, initial=Hole()*Literal('0')*Literal('1')*Literal('0')*Literal('1')*Hole(), pause=False, verbose=False)
    assert pattern == '(.)*0101(.)*'
