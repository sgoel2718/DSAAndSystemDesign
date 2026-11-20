"""Helper for ML & AI concept cards (same shape as System Design cards, plus runnable Python)."""
LEVELS = ("Basic", "Intermediate", "Advanced")


def M(id, title, level, what, body, analogy="", example="", code="", net=False, demo=None, diagram=None, say=(), see=()):
    """id: unique (prefixed 'm-'); code: runnable Python shown on the card; net=True if it needs internet/API keys
    (then it is only syntax-checked here); demo: id of an in-browser live demo; say: [(interviewer question, answer)]."""
    assert level in LEVELS, (id, level)
    assert id.startswith("m-"), id
    return dict(id=id, title=title, level=level, what=what, body=body.strip(), analogy=analogy, example=example,
                tips=[], code=code.strip("\n"), net=net, demo=demo, diagram=diagram,
                say=[dict(p="Interviewer: " + q, a=a) for q, a in say], see=list(see))
