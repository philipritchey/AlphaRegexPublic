from main.main import matches_all, matches_any, search, get_literals, inflate, main

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

def test_search_starts_with_0():
    P = {'0', '00', '01', '000', '001', '010', '011'}
    N = {'', '1', '10', '11', '100', '101', '110', '111'}
    pattern = search(P, N)
    assert pattern == '0.*'

def test_search_ends_with_01():
    P = {'01', '001', '101', '0001', '0101', '1001', '1101'}
    N = {'', '0', '1', '00', '10', '11', '100', '110', '111'}
    pattern = search(P, N)
    assert pattern == '.*01'

# too slow (not yet observed to terminate, t > 30s)
# def test_search_contains_0101():
#     P = {'0101', '00101', '01010', '10101', '01011'}
#     N = {'0000', '0001', '0010', '0011', '0100', '0110', '0111', '1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111'}
#     pattern = search(P, N)
#     assert pattern == '(.)*0101(.)*'

def test_search_begin_with_1_end_with_0():
    P = {'10', '100', '110', '1000', '1010', '1100', '1110'}
    N = {'0', '1', '00', '01', '11', '000', '001', '010', '011', '101', '111'}
    pattern = search(P, N)
    assert pattern == '1.*0'

def test_search_length_at_least_3_and_3rd_symbol_is_0():
    P = {'000', '010', '100', '110', '0000', '0001', '0100', '0101', '1000', '1001', '1100', '1101'}
    N = {'0', '1', '00', '01', '10', '11', '001', '011', '101', '111', '0010', '0011', '0110', '0111'}
    pattern = search(P, N)
    assert pattern == '..0.*'

def test_search_length_is_a_multiple_of_3():
    P = {'', '000', '001', '010', '011', '100', '101', '110', '111', '000000', '010101', '000111', '000111010'}
    N = {'0', '1', '00', '01', '10', '11', '0010', '0011', '0110', '0111'}
    pattern = search(P, N)
    assert pattern == '(...)*'

# too slow (t > 500s)
# def test_search_each_0_followed_by_some_1s():
#     P = {'', '01', '011', '0101', '011', '10101', '101', '1101', '111', '010110111011110111110111111', '010101', '01010111', '011101101110101'}
#     N = {'0', '10', '00', '010', '10', '110', '0010', '0011', '0110', '0111'}
#     pattern = search(P, N)
#     assert pattern == '((0)?1)*'

def test_no5_length_at_least3_and_third_0():
    P = {'XX0', 'XX0X', 'XX0XX'}
    N = {'X', 'XX', 'XX1', 'XX1X'}
    pattern = search(P, N).replace('X', '.')
    assert pattern == '..0.*'

def test_inflate():
    e = 'X'
    es = inflate(e,'01')
    assert es == ['0', '1']

    e = 'XX'
    es = inflate(e, '01')
    assert es == ['00', '01', '10', '11']

def test_main():
    main('../benchmarks/no01_start_with_0')
    # main('../benchmarks/no2_end_with_01')
    main('../benchmarks/no03_substring_0101')
    # main('../benchmarks/no4_begin_1_end_0')
    # main('../benchmarks/no5_length_at_least3_and_third_0')
