from main.helpers import matches_all, matches_any, get_literals, inflate

def test_matches_all():
  examples = {'0', '00', '01', '001'}
  pattern = '0.*'
  assert matches_all(pattern, examples)
  pattern = '0*1'
  assert not matches_all(pattern, examples)

def test_matches_any():
  examples = {'0', '00', '01', '001'}
  assert matches_any('00', examples)
  assert not matches_any('10', examples)


def test_get_literals():
  examples = {'0', '00', '01', '001'}
  assert get_literals(examples) == '.01'

def test_inflate():
  e = 'X'
  es = inflate(e,'01')
  assert es == ['0', '1']

  e = 'XX'
  es = inflate(e, '01')
  assert es == ['00', '01', '10', '11']
