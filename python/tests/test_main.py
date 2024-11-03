'''
tests for main.py
'''

from main.main import main, read_examples

def test_main():
  '''
  tests for main
  '''
  main(read_examples('../benchmarks/no01_start_with_0'))
  # main('../benchmarks/no02_end_with_01')
  main(read_examples('../benchmarks/no03_substring_0101'))
  # main('../benchmarks/no04_begin_1_end_0')
  # main('../benchmarks/no05_length_at_least3_and_third_0')

# still too slow
# def test_no07_zeros_divisible_by_3():
#   main('../benchmarks/no07_zeros_divisible_by_3')
