import re

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
  literals = 'X.'
  for example in examples:
    for symbol in example:
      if symbol not in literals:
        literals += symbol
  # 'X' is same thing as '.', so exclude it
  return literals[1:]

def inflate(example: str, alphabet: str) -> list[str]:
  '''
  replace each X with a in alphabet

  Args:
    example (set[str]): example to inflate
    alphabet (str): alphabet to use

  Returns:
    list[str]: inflated examples
  '''
  if 'X' not in example:
    return [example]
  inflated_examples = []
  for a in alphabet:
    es = inflate(example.replace('X', a, 1), alphabet)
    inflated_examples.extend(es)
  return inflated_examples

def inflate_all(example_set: set[str], alphabet: str) -> set[str]:
  '''
  replace each X with a in alphabet

  Args:
    example_set (set[str]): examples to inflate
    alphabet (str): alphabet to use

  Returns:
    set[str]: inflated set of examples
  '''
  s: set[str] = set()
  for example in example_set:
    inflated_examples = inflate(example, alphabet)
    for e in inflated_examples:
      s.add(e)
  return s
