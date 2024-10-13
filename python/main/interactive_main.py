'''
Interactive Main
'''
import heapq
from main.partial_regex import PartialRegexNode, Hole
from main.helpers import matches_all, matches_any, inflate_all

def interactive_search(P: set[str], N: set[str], alphabet: str = '01', **kwargs) -> str:
  pause = kwargs['pause'] if 'pause' in kwargs else True
  verbose = kwargs['verbose'] if 'verbose' in kwargs else True
  initial = kwargs['initial'] if 'initial' in kwargs else Hole()
  N = inflate_all(N, alphabet)
  print(f'{N=}')
  q: list[PartialRegexNode] = []
  heapq.heappush(q, initial)
  v_pre: set[PartialRegexNode] = set()
  v_post: set[PartialRegexNode] = set()
  steps: int = 0
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
          print('  PASS')
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
      for next_state in state.next_states(alphabet):
        if verbose:
          print(f'  {next_state}, {next_state.cost()}', end='')
        if next_state not in v_pre:
          heapq.heappush(q, next_state)
          v_pre.add(next_state)
          if verbose:
            print(' (new)')
        elif verbose:
          print()

if __name__ == '__main__':
  P = {'XXX', 'XXXXXX'} # not OK to have only Xs in P because we need to know how to inflate N
  N = {'X', 'XX', 'XXXX'}
  pattern = interactive_search(P, N, '01', pause=False)
  print(f'{pattern=}')
  assert pattern == '(...)*'

  # P = {'XX0', 'XX0X', 'XX0XX'}  # OK to have X in P because . will match it
  # N = {'X', 'XX', 'XX1', 'XX1X'}  # not OK to have X in N since no literals will match it
  # pattern = interactive_search(P, N, pause=False)
  # print(f'{pattern=}')
  # assert pattern == '..0(.)*'

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
  #assert pattern == '(.)*0101(.)*'
