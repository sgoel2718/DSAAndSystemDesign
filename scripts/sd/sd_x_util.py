"""Helpers for the detailed 'explained step by step, with diagrams' layer of the System Design section.

Each card gets X(id, *blocks). Blocks render in order (see sd_viz.js). All estimate numbers in CALC are computed here.
"""
EXPLAIN = {}


def X(id, *blocks):
    assert id not in EXPLAIN, "duplicate explain " + id
    EXPLAIN[id] = dict(blocks=[b for b in blocks if b])


def P(md): return dict(t="md", md=md.strip())
def H(md): return dict(t="h", md=md)
def AN(md): return dict(t="analogy", md=md.strip())
def KEY(md, title="Key idea"): return dict(t="key", md=md.strip(), title=title)
def FLOW(title, rows, edges, caption=""): return dict(t="flow", title=title, caption=caption, spec=dict(rows=rows, edges=edges))
def SEQ(title, actors, msgs, caption=""):
    out = []
    for m in msgs:
        if isinstance(m, dict): out.append(m); continue
        m = list(m) + [""] * (5 - len(m)); out.append(m[:5])
    return dict(t="seq", title=title, caption=caption, spec=dict(actors=actors, msgs=out))
def NOTE(actors, text): return dict(note=list(actors) if isinstance(actors, (list, tuple)) else [actors], text=text)
def UML(title, rows, classes, rels, caption=""):
    cl = {}
    for name, spec in classes.items():
        k, f, m = spec if len(spec) == 3 else ("class",) + tuple(spec)
        cl[name] = dict(k=k, f=list(f), m=list(m))
    return dict(t="uml", title=title, caption=caption, spec=dict(rows=rows, classes=cl, rels=rels))
def STATE(title, rows, edges, caption=""): return dict(t="state", title=title, caption=caption, spec=dict(rows=rows, edges=edges))
def ER(title, tables, links=(), caption=""):
    return dict(t="er", title=title, caption=caption, spec=dict(tables=[dict(name=n, store=s, cols=[list(c) + [""] * (3 - len(c)) for c in cols], note=note) for n, s, cols, note in tables], links=list(links)))
def TABLE(title, head, rows, caption=""): return dict(t="table", title=title, caption=caption, spec=dict(head=head, rows=[list(map(str, r)) for r in rows]))
def BARS(title, items, log=False, caption=""): return dict(t="bars", title=title, caption=caption, spec=dict(items=[list(i) for i in items], log=log))
def CODE(title, code, lang="java"): return dict(t="code", title=title, code=code.strip("\n"), lang=lang)
def OUT(text, title=""): return dict(t="out", text=text, title=title)


def human(v, unit=""):
    if unit in ("B", "B/s", "B/day"):
        for u, s in (("EB", 1e18), ("PB", 1e15), ("TB", 1e12), ("GB", 1e9), ("MB", 1e6), ("KB", 1e3)):
            if abs(v) >= s: return f"{v / s:,.1f}".rstrip("0").rstrip(".") + " " + u + unit[1:]
        return f"{v:,.0f} B" + unit[1:]
    for u, s in (("trillion", 1e12), ("billion", 1e9), ("million", 1e6)):
        if abs(v) >= s: return f"{v / s:,.1f}".rstrip("0").rstrip(".") + " " + u + (" " + unit if unit else "")
    txt = f"{v:,.0f}" if abs(v) >= 100 or float(v).is_integer() else (f"{v:,.1f}" if abs(v) >= 10 else f"{v:,.2f}").rstrip("0").rstrip(".")
    return txt + (" " + unit if unit else "")


def CALC(title, rows, caption=""):
    """rows: (quantity, python expression shown and evaluated, unit, note). Earlier results are available by name via 'name=' prefix."""
    env, out = {}, []
    for r in rows:
        q, expr, unit, note = (list(r) + ["", ""])[:4]
        name, shown = None, expr
        if "=" in expr.split("(")[0] and not expr.startswith("="):
            name, expr = [s.strip() for s in expr.split("=", 1)]
        v = eval(expr, {"math": __import__("math")}, env)
        if name: env[name] = v
        out.append([q, shown.replace("**", "^").replace("*", "×"), human(v, unit), note])
    return dict(t="calc", title=title, caption=caption, spec=dict(rows=out))
