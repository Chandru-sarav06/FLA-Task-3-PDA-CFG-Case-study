# FLA Task 3 - Case Studies with Pushdown Automata and Context-Free Grammars

**CLA-2, Task 3 - 21CSC301T Formal Language and Automata (SRM IST, Tiruchirappalli)**
Author: **Chandru M S** (RA2411026050028) - individual work

| Case study | Grammar / PDA | Point demonstrated |
|---|---|---|
| A. Palindromes over {a,b} | `S -> aSa | bSb | a | b | eps`, 3-state **nondeterministic** PDA | the PDA must *guess* the middle; with a centre marker (`w c w^R`) a DPDA suffices |
| B. HTML/XML tag nesting | `Doc -> Elem Doc | eps`, `Elem -> T | <t> Doc </t>` ; stack-of-tag-names machine | real-world deterministic stack machine with precise error reporting |
| C. Programming-language syntax: dangling else | ambiguous G1 and repaired G2 | ambiguity detection by parse-tree counting; same language, 71/71 strings unambiguous after the fix |

Also: pumping-lemma-style argument and a measured "finite memory vs stack" experiment (`why_stack.py`),
a generic **CFG -> PDA** construction, a bounded BFS PDA simulator with traces, leftmost derivations and parse trees.

## Run
```bash
pip install -r requirements.txt
python -m pytest -q                 # 35 tests
python tools/verify.py              # bounded-exhaustive sweeps -> results/verification.json
python tools/make_figures.py        # needs Graphviz `dot`
python -m fla_pda.cli pal abba      # see cli.py for all commands
```

## Layout
```
fla_pda/cfg.py          Grammar: parse text, count parse trees (ambiguity), derivations, generation, CFG->PDA
fla_pda/pda.py          NPDA simulator (BFS, bounded, returns an accepting trace)
fla_pda/palindromes.py  case study A
fla_pda/markup.py       case study B
fla_pda/dangling_else.py case study C (G1, G2)
fla_pda/why_stack.py    DFA size vs nesting depth
tests/  tools/  results/  docs/figures/
```
