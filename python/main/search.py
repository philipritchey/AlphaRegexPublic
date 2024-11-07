'''
Search
'''

import heapq
from main.partial_regex import PartialRegexNode, Hole, opt, Star, Union, Literal, Concatenation
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
  P = inflate_all(P, alphabet)
  N = inflate_all(N, alphabet)
  # print(f"{P=}")
  # print(f"{N=}")
  q: list[PartialRegexNode] = []
  v_pre: set[PartialRegexNode] = {Hole()}
  # preload queue with next states after Hole (which is never a solution)
  for next_state in Hole().next_states(alphabet):
    heapq.heappush(q, next_state)
    v_pre.add(next_state)
  # solution_cost_limit = None
  # target_state = Star(Union(Literal('0'), Concatenation(Literal('1'), Hole())))
  while True:
    state = heapq.heappop(q)
    # if state == target_state:
    #   print()
    #   print(f'[DEBUG] {state=} {state} {state.cost()}')
    # print(state.cost())
    if state.is_solution(P, N):  # and solution_cost_limit and state.cost() <= solution_cost_limit:
      return str(opt(state))
    if not state.is_dead(P, N):
      # expand and add to queue
      for next_state in state.next_states(alphabet):
        # if state == target_state:
        #   print(f'        {next_state=} {next_state}', end='')
        # if next_state.cost() > cost_limit:
        #   if state == target_state:
        #     print(f"{next_state} is too expensive: {next_state.cost()}")
        #   continue
        if next_state not in v_pre:
          heapq.heappush(q, next_state)
          v_pre.add(next_state)
    #     print(' added')
      # else:
      #   print(' NOT added')
    # else:
    #   if state == target_state:
    #     print('        dead')
