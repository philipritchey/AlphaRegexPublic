'''
main
'''
import sys
from cProfile import Profile
from pstats import SortKey, Stats
from time import time
from main.search import search

def main(examples: str) -> None:
  '''
  the entry point of the program

  Args:
      examples (str): path to file containing positive and negative examples.
                      first line is description of language.
                      "++" on a line begins positive exmaples.
                      "--" on a line begins negatvie examples.
  '''
  P: set[str] = set()
  N: set[str] = set()
  with open(examples, 'r', encoding="utf-8") as f:
    description = f.readline().strip()
    print(f'{description} | ', end='', flush=True)
    active_set = P
    for line in f:
      line = line.strip()
      if line == '++':
        active_set = P
      elif line == '--':
        active_set = N
      else:
        active_set.add(line)
  t1 = time()
  pattern = search(P, N)
  t2 = time()
  dt = t2 - t1
  units = 's'
  if dt < 1:
    dt *= 1000
    units = 'ms'
  print(f'{pattern} | {dt:0.2f} {units}')

if __name__ == '__main__':
  if len(sys.argv) == 1:
    print('error: missing required examples filename')
    sys.exit(1)
  examples = sys.argv[1]
  # print(f'{examples=}')
  with Profile() as profile:
    main(examples)
    (
      Stats(profile)
      .strip_dirs()
      .sort_stats(SortKey.CALLS)
      .print_stats()
    )