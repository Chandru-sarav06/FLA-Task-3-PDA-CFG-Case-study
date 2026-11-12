import itertools
import pytest
from fla_pda.cfg import Grammar
from fla_pda.palindromes import *
from fla_pda.markup import *
from fla_pda.dangling_else import *
from fla_pda.why_stack import *

# ---------------------------------------------------------------- A palindromes
NP, DP = pda_nondeterministic(), pda_marker()

@pytest.mark.parametrize("s", ["", "a", "b", "aa", "aba", "abba", "baab", "abbbba"])
def test_palindromes_accepted(s): assert NP.accepts(s) and CFG.accepts(s)

@pytest.mark.parametrize("s", ["ab", "abb", "abab", "baa", "aabb", "abaab"])
def test_palindromes_rejected(s): assert not NP.accepts(s) and not CFG.accepts(s)

def test_nondeterminism_flag():
    assert not NP.is_deterministic and DP.is_deterministic

def test_palindrome_exhaustive_len_le_8():
    for L in range(9):
        for t in itertools.product("ab", repeat=L):
            s = "".join(t)
            assert NP.accepts(s) == is_palindrome(s)
            assert CFG.count_parses(s) == (1 if is_palindrome(s) else 0)   # unambiguous grammar

def test_marker_dpda():
    assert DP.accepts("abcba") and DP.accepts("c") and not DP.accepts("abcab") and not DP.accepts("abba")

def test_trace_shows_stack_discipline():
    ok, tr = NP.run("abba")
    assert ok and tr[0][2] == ("Z",) and tr[-1][2] == ("Z",) and tr[-1][0] == "q2"

# ---------------------------------------------------------------- B markup
@pytest.mark.parametrize("s", ["<p></p>", "<html><body><p>hi</p></body></html>", "<div><br/><b>x</b></div>",
                               "plain text", "<ul><li>a</li><li>b</li></ul>"])
def test_markup_ok(s): assert check_markup(s).ok

@pytest.mark.parametrize("s,frag", [("<a><b></a></b>", "expected </b>"), ("</a>", "empty stack"),
                                    ("<a><b></b>", "unclosed"), ("<p>x</q>", "expected </p>"), ("<div><p>", "unclosed")])
def test_markup_bad(s, frag):
    r = check_markup(s); assert not r.ok and frag in r.error

def test_markup_stack_vs_cfg_small():
    G = tag_grammar(["a", "b"]); toks = ["<a>", "</a>", "<b>", "</b>", "T"]
    for L in range(7):
        for t in itertools.product(toks, repeat=L):
            assert check_tokens(t) == G.accepts(t)

# ---------------------------------------------------------------- C dangling else
def test_classic_string_is_ambiguous_in_G1_only():
    assert AMBIGUOUS.count_parses(CLASSIC) == 2 and UNAMBIGUOUS.count_parses(CLASSIC) == 1

def test_same_language_and_G2_unambiguous():
    for L in range(1, 15):
        g1 = {s for s in AMBIGUOUS.generate(L)}; g2 = {s for s in UNAMBIGUOUS.generate(L)}
        assert g1 == g2
        assert all(UNAMBIGUOUS.count_parses(s) == 1 for s in g2)

def test_two_trees_found():
    assert len(AMBIGUOUS.parse_trees(CLASSIC)) == 2

def test_cfg_to_pda_accepts_classic():
    assert AMBIGUOUS.to_pda().accepts(CLASSIC) and not AMBIGUOUS.to_pda().accepts(["if", "c", "then"])

def test_leftmost_derivation():
    d = UNAMBIGUOUS.leftmost_derivation(CLASSIC)
    assert d[0] == ("Stmt",) and d[-1] == tuple(CLASSIC)

# ---------------------------------------------------------------- why a stack
def test_dfa_size_grows_with_depth():
    assert [bounded_depth_dfa_states(k) for k in (1, 2, 3)] == [3, 4, 5]
    assert stack_machine_max_depth("((()))")[0]
