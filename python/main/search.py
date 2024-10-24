'''
Search
'''

import heapq
from main.partial_regex import PartialRegexNode, Hole
from main.helpers import inflate_all

def search(P: set[str], N: set[str], alphabet: str = '01') -> str:
  '''
  The search algorithm.
  Finds a regex that matches all positive and no negative examples.

  Args:
      P (set[str]): positive examples
      N (set[str]): negative examples
      alphabet (str, optional): the input alphabet. Defaults to '01'.

  Returns:
      str: a regex which matches all positive but no negative examples
  '''
  N = inflate_all(N, alphabet)
  q: list[PartialRegexNode] = []
  heapq.heappush(q, Hole())
  v_pre: set[PartialRegexNode] = set()
  v_post: set[PartialRegexNode] = set()
  while True:
    state = heapq.heappop(q)
    # print(f'[DEBUG] {state=} {state}')
    if state in v_post:
      # print('        skipped')
      continue
    v_post.add(state)
    if state.is_solution(P, N):
      return str(state)
    if not state.is_dead(P, N):
      # expand and add to queue
      for next_state in state.next_states(alphabet):
        # print(f'        {next_state=} {next_state}', end='')
        if next_state not in v_pre:
          heapq.heappush(q, next_state)
          v_pre.add(next_state)
    #       print(' added')
    #     else:
    #       print(' NOT added')
    # else:
    #   print('        dead')
