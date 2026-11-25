"""Beginner lessons for the ML concept cards.

Each lesson assumes the reader knows nothing about the topic. It goes, in order:
why it matters -> the idea in plain words -> small worked steps with real numbers -> try it yourself ->
the words people use -> code (only now, explained line by line) -> check yourself.
The original dense card content stays available under a fold below the lesson.
"""
LESSONS = {}
import sys as _s, os as _o
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))


def L(id, hook, why, idea, steps, tryit, words, code_intro, code, check, net=False):
    """hook: one plain sentence shown on the closed card; steps: [(heading, markdown)];
    tryit: (question, answer); words: [(term, plain meaning)]; check: [(question, answer)]."""
    assert id not in LESSONS, id
    assert len(steps) >= 2 and len(check) >= 2, id
    LESSONS[id] = dict(hook=hook, why=why.strip(), idea=idea.strip(), steps=[dict(h=h, md=m.strip()) for h, m in steps],
                       tryq=tryit[0].strip(), trya=tryit[1].strip(), words=[dict(t=t, m=m) for t, m in words],
                       code_intro=code_intro.strip(), code=code.strip("\n"), net=net, check=[dict(q=q, a=a) for q, a in check])
