"""Registry of theory interview questions (with model answers) for every System Design concept, HLD and LLD card."""
IQ = {}
LEVELS = {"B": "Basic", "I": "Intermediate", "A": "Advanced"}


def Q(id, *items):
    """items: (level 'B'|'I'|'A', question, answer)."""
    assert id not in IQ, "duplicate questions for " + id
    assert 5 <= len(items) <= 12, f"{id}: {len(items)} questions"
    for lv, q, a in items: assert lv in LEVELS and q.strip() and a.strip(), (id, q)
    IQ[id] = [dict(lv=lv, q=q.strip(), a=a.strip()) for lv, q, a in items]
