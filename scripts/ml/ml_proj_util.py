"""Helpers for end-to-end ML projects (each project = a small repository you build step by step)."""
LEVELS = {"full": "Verified end to end here on the real data",
          "smoke": "Pipeline verified here with --smoke (tiny data/model); the full run needs a GPU and/or internet (Colab)",
          "static": "Code checked (syntax + undefined names); needs internet, a GPU or an API key to run — use Colab"}


def S(title, text, file=None, code="", lang=None):
    """One build step. file = path inside the project folder (written to disk); lang inferred from the extension."""
    if lang is None:
        lang = "python" if (file or "").endswith(".py") else "bash" if not file else (file.rsplit(".", 1)[-1] if "." in file else "text")
    return dict(title=title, text=text.strip(), file=file, code=code.strip("\n") + "\n" if code else "", lang=lang)


def P(id, title, tab, level, time, run, what, build, skills, data, arch, steps, check=(), talk=(), errors=(), extend=(), see=(), verify="full"):
    assert id.startswith("p-"), id
    assert verify in LEVELS
    files = [s["file"] for s in steps if s["file"]]
    if any(f.startswith("tests/") for f in files) and "pytest.ini" not in files:
        i = max(i for i, s in enumerate(steps) if s["file"] == "requirements.txt") + 1 if "requirements.txt" in files else 0
        steps = steps[:i] + [S("pytest settings", "Lets the tests import your modules from the project root (run `pytest -q` from there).", "pytest.ini",
                                 "[pytest]\npythonpath = .\ntestpaths = tests", "text")] + steps[i:]
        files.append("pytest.ini")
    assert len(files) == len(set(files)), (id, [f for f in files if files.count(f) > 1])
    tree = _tree(files)
    return dict(id=id, title=title, tab=tab, level=level, time=time, run=run, what=what, build=list(build), skills=list(skills), data=data,
                arch=list(arch), steps=steps, tree=tree, check=list(check), talk=list(talk), errors=[list(e) for e in errors],
                extend=list(extend), see=list(see), verify=verify)


def _tree(files):
    root = {}
    for f in sorted(files):
        node = root
        for part in f.split("/"):
            node = node.setdefault(part, {})
    lines = []
    def walk(node, prefix):
        items = sorted(node.items(), key=lambda kv: (not kv[1], kv[0]))
        for i, (name, child) in enumerate(items):
            last = i == len(items) - 1
            lines.append(prefix + ("└── " if last else "├── ") + name + ("/" if child else ""))
            if child:
                walk(child, prefix + ("    " if last else "│   "))
    walk(root, "")
    return "project/\n" + "\n".join(lines)
