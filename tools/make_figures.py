import json, subprocess, sys
sys.path.insert(0, ".")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fla_pda.dangling_else import *

F = "docs/figures/"
def render(dot, name):
    open(F + name + ".dot", "w").write(dot)
    subprocess.run(["dot", "-Tpng", "-Gdpi=150", F + name + ".dot", "-o", F + name + ".png"], check=True)

# Fig: palindrome NPDA
render("""digraph G { rankdir=LR; node [shape=circle]; edge [fontsize=9]; s [shape=point,width=.1]; s->q0;
 q2 [shape=doublecircle];
 q0 -> q0 [label="x, any / x·any   (push, x∈{a,b})"];
 q0 -> q1 [label="ε, any / any   (guess even centre)"];
 q0 -> q1 [label="x, any / any   (consume odd centre)"];
 q1 -> q1 [label="x, x / ε   (match & pop)"];
 q1 -> q2 [label="ε, Z / Z"]; }""", "fig_pal_npda")
# Fig: marker DPDA
render("""digraph G { rankdir=LR; node [shape=circle]; edge [fontsize=9]; s [shape=point,width=.1]; s->q0; q2 [shape=doublecircle];
 q0 -> q0 [label="a|b, any / push"]; q0 -> q1 [label="c, any / any"]; q1 -> q1 [label="x, x / ε"]; q1 -> q2 [label="ε, Z / Z"]; }""", "fig_marker_dpda")
# Fig: markup control flow
render("""digraph G { rankdir=TB; node [shape=box, style=rounded]; edge [fontsize=10];
 start [label="read next token", shape=ellipse];
 start -> open [label="<t>"]; start -> close [label="</t>"]; start -> text [label="text / <br/>"]; start -> end [label="end of input"];
 open [label="push t"]; open -> start; text [label="ignore"]; text -> start;
 close [label="stack empty?", shape=diamond, style=""]; close -> e1 [label="yes"]; close -> cmp [label="no"];
 cmp [label="top == t ?", shape=diamond, style=""]; cmp -> pop [label="yes"]; cmp -> e2 [label="no"];
 pop [label="pop"]; pop -> start;
 end [label="stack empty?", shape=diamond, style=""]; end -> acc [label="yes"]; end -> e3 [label="no"];
 e1 [label="REJECT: stray closer", style="rounded,filled", fillcolor="#fde2e2"]; e2 [label="REJECT: mismatch", style="rounded,filled", fillcolor="#fde2e2"];
 e3 [label="REJECT: unclosed tag", style="rounded,filled", fillcolor="#fde2e2"]; acc [label="ACCEPT", style="rounded,filled", fillcolor="#e2f5e2"]; }""", "fig_markup_flow")
# Fig: two parse trees
def tree_dot(t, name):
    lines, n = [f"digraph T {{ node [shape=plaintext, fontsize=11]; edge [arrowhead=none];"], [0]
    def walk(x):
        n[0] += 1; me = f"n{n[0]}"
        if isinstance(x, str):
            lines.append(f'{me} [label="{x}", fontname="Courier-Bold"];'); return me
        lines.append(f'{me} [label="{x[0]}"];')
        for c in x[1]:
            lines.append(f"{me} -> {walk(c)};")
        return me
    walk(t); lines.append("}"); render("\n".join(lines), name)
trees = AMBIGUOUS.parse_trees(CLASSIC)
for i, t in enumerate(trees): tree_dot(t, f"fig_dangling_tree{i+1}")
uni = UNAMBIGUOUS.parse_trees(CLASSIC)[0]; tree_dot(uni, "fig_dangling_fixed")
# Charts
v = json.load(open("results/verification.json"))
ks = list(map(int, v["bounded_depth_dfa_states"].keys())); vals = list(v["bounded_depth_dfa_states"].values())
fig, ax = plt.subplots(figsize=(6.5, 3.4)); ax.plot(ks, vals, "o-", label="DFA for depth ≤ k"); ax.axhline(1, ls="--", c="grey", label="PDA control states (1; stack grows)")
ax.set_xlabel("maximum nesting depth k"); ax.set_ylabel("states needed"); ax.legend(); ax.set_title("Finite memory vs stack"); plt.tight_layout(); plt.savefig(F + "fig_dfa_vs_depth.png", dpi=150)
rows = [r for r in v["dangling_else"]["by_length"] if r["strings"]]
fig, ax = plt.subplots(figsize=(7, 3.4)); xs = [r["length"] for r in rows]
ax.bar([x - 0.2 for x in xs], [r["g1_ambiguous"] for r in rows], 0.4, label="G1 (ambiguous)  strings with >1 parse tree")
ax.bar([x + 0.2 for x in xs], [r["g2_ambiguous"] for r in rows], 0.4, label="G2 (revised)  strings with >1 parse tree")
ax.set_xlabel("token length"); ax.set_ylabel("ambiguous strings"); ax.legend(fontsize=8); ax.set_title("Ambiguity before and after the grammar fix"); plt.tight_layout(); plt.savefig(F + "fig_ambiguity_chart.png", dpi=150)
print("ok")
