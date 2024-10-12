import sys
from time import time
from main.search import search

def main(examples: str) -> None:
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
  t1 = time()
  pattern = search(P, N)
  t2 = time()
  dt = t2 - t1
  units = 's'
  if dt < 1:
    dt *= 1000
    units = 'ms'
  print(f'{description} | {pattern} | {dt:0.2f} {units}')

if __name__ == '__main__':
  if len(sys.argv) == 1:
    print('error: missing required examples filename')
    sys.exit(1)
  examples = sys.argv[1]
  # print(f'{examples=}')
  main(examples)
