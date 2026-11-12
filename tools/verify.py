import itertools, json, sys, time
sys.path.insert(0, ".")
from fla_pda.palindromes import *
from fla_pda.markup import *
from fla_pda.dangling_else import *
from fla_pda.why_stack import *

R = {}
# --- A palindromes
npda, dpda = pda_nondeterministic(), pda_marker()
n = bad_pda = bad_cfg = amb = cfgpda_bad = 0
cfgpda = CFG.to_pda()
for L in range(0, 11):
    for t in itertools.product("ab", repeat=L):
        s = "".join(t); n += 1; exp = is_palindrome(s)
        bad_pda += npda.accepts(s) != exp
        c = CFG.count_parses(s); bad_cfg += (c > 0) != exp; amb += c > 1
        if L <= 8: cfgpda_bad += cfgpda.accepts(s) != exp
R["palindromes"] = dict(strings=n, npda_mismatch=bad_pda, cfg_mismatch=bad_cfg, ambiguous_strings=amb,
                        cfg_derived_pda_mismatch_len_le_8=cfgpda_bad, npda_deterministic=npda.is_deterministic)
n = bad = 0
for L in range(0, 9):
    for t in itertools.product("abc", repeat=L):
        s = "".join(t); n += 1
        exp = s.count("c") == 1 and is_palindrome(s.replace("c", "")) and s.index("c") == len(s) // 2 and len(s) % 2 == 1
        bad += dpda.accepts(s) != exp
R["marker"] = dict(strings=n, dpda_mismatch=bad, dpda_deterministic=dpda.is_deterministic)

# --- B markup
G = tag_grammar(["a", "b"]); toks = ["<a>", "</a>", "<b>", "</b>", "T"]
n = bad = amb = acc = 0
for L in range(0, 8):
    for t in itertools.product(toks, repeat=L):
        n += 1; ok = check_tokens(t); c = G.count_parses(t)
        bad += ok != (c > 0); amb += c > 1; acc += ok
R["markup"] = dict(strings=n, accepted=acc, stack_vs_cfg_mismatch=bad, ambiguous=amb)
gp = G.to_pda(); n = bad = 0
for L in range(0, 6):
    for t in itertools.product(toks, repeat=L):
        n += 1; bad += gp.accepts(t) != check_tokens(t)
R["markup_cfg_pda"] = dict(strings=n, mismatch=bad)

# --- C dangling else
rows = []
tot1 = tot2 = amb1 = amb2 = 0
same = True
for L in range(1, 21):
    g1 = {s for s in AMBIGUOUS.generate(L) if len(s) == L}
    g2 = {s for s in UNAMBIGUOUS.generate(L) if len(s) == L}
    same &= g1 == g2
    a1 = sum(AMBIGUOUS.count_parses(s) > 1 for s in g1)
    a2 = sum(UNAMBIGUOUS.count_parses(s) > 1 for s in g2)
    tot1 += len(g1); tot2 += len(g2); amb1 += a1; amb2 += a2
    rows.append(dict(length=L, strings=len(g1), g1_ambiguous=a1, g2_ambiguous=a2))
R["dangling_else"] = dict(same_language_len_le_20=same, g1_total=tot1, g1_ambiguous=amb1, g2_total=tot2, g2_ambiguous=amb2,
                          classic_parses_g1=AMBIGUOUS.count_parses(CLASSIC), classic_parses_g2=UNAMBIGUOUS.count_parses(CLASSIC), by_length=rows)
gp1 = AMBIGUOUS.to_pda(); gp2 = UNAMBIGUOUS.to_pda()
R["dangling_else"]["cfg_pda_accepts_classic"] = [gp1.accepts(CLASSIC), gp2.accepts(CLASSIC)]
# --- why a stack
R["bounded_depth_dfa_states"] = {k: bounded_depth_dfa_states(k) for k in (1, 2, 3, 5, 10, 20, 50)}
json.dump(R, open("results/verification.json", "w"), indent=2)
print(json.dumps({k: v for k, v in R.items() if k != "dangling_else"}, indent=1))
d = R["dangling_else"]; print({k: v for k, v in d.items() if k != "by_length"})
