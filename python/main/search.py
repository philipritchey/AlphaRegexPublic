import heapq
from main.partial_regex import PartialRegexNode, opt, Hole
from main.helpers import matches_all, matches_any, inflate_all

def solution(state: PartialRegexNode, P: set[str], N: set[str]) -> bool:
  if state.holes() > 0:
    return False
  pattern = str(opt(state))
  # print(f'[DEBUG] {pattern=}')
  return matches_all(pattern, P) and not matches_any(pattern, N)

def dead(state: PartialRegexNode, P: set[str], N: set[str]) -> bool:
  # check for deadness
  o = state.overapproximation()
  s = opt(opt(o))
  overapproximation = str(s)
  if not matches_all(overapproximation, P):
    # dead
    return True

  u = state.underapproximation()
  s = opt(opt(u))
  underapproximation = str(s)
  if matches_any(underapproximation, N):
    # dead
    return True

  # redundant states
  A = state.unroll().split()
  for e in A:
    overapproximation = opt(opt(e.overapproximation()))
    if not matches_any(str(overapproximation), P):
      # dead
      return True
  return False

def search(P: set[str], N: set[str], alphabet: str = '01') -> str:
  N = inflate_all(N, alphabet)
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
      for next_state in state.next_states(alphabet):
        if next_state not in v_pre:
          heapq.heappush(q, next_state)
          v_pre.add(next_state)
