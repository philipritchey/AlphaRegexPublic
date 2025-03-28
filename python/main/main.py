'''
main
'''
import sys
from cProfile import Profile
from pstats import SortKey, Stats
from time import time
from main.search import search

def read_examples(examples_file: str) -> dict[str, set[str]]:
  '''
  read examples

  Args:
      examples_file (str): path to examples file

  Returns:
      dict[str, set[str]]: P: positive examples, N: negative examples
  '''
  examples: dict[str, set[str]] = {}
  examples['P'] = set()
  examples['N'] = set()
  with open(examples_file, 'r', encoding="utf-8") as f:
    description = f.readline().strip()
    print(f'{description} | ', end='', flush=True)
    active_set = examples['P']
    for line in f:
      line = line.strip()
      if line == '++':
        active_set = examples['P']
      elif line == '--':
        active_set = examples['N']
      else:
        active_set.add(line)
  return examples

def main(examples: dict[str, set[str]]) -> None:
  '''
  the entry point of the program

  Args:
      examples (str): path to file containing positive and negative examples.
                      first line is description of language.
                      "++" on a line begins positive exmaples.
                      "--" on a line begins negatvie examples.
  '''
  t1 = time()
  pattern = search(examples['P'], examples['N'])
  t2 = time()
  dt = t2 - t1
  units = 's'
  if dt < 1:
    dt *= 1000
    units = 'ms'
  print(f'{pattern} | {dt:0.2f} {units}')

if __name__ == '__main__': # pragma: no cover
  # [--profile] <filename>
  if len(sys.argv) == 1:
    print('error: missing required examples filename')
    sys.exit(1)
  EXAMPLES = read_examples(sys.argv[-1])
  # print(f'{examples=}')
  if '--profile' in sys.argv:
    with Profile() as profile:
      main(EXAMPLES)
      (
        Stats(profile)
        .strip_dirs()
        .sort_stats(SortKey.CALLS)
        .print_stats()
      )
  else:
    main(EXAMPLES)