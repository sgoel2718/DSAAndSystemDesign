"""Deeper layer + end-to-end walkthrough for each concept card."""
D = {}


def X(id, intuition, maths, worked, mistakes, use, avoid, data, steps, code, net=False):
    """intuition/maths/worked: markdown; mistakes/use/avoid/steps: lists; data: dataset description; code: runnable e2e script."""
    assert id not in D, id
    assert len(steps) >= 4, id
    D[id] = dict(intuition=intuition.strip(), maths=maths.strip(), worked=worked.strip(), mistakes=list(mistakes), use=list(use), avoid=list(avoid),
                 data=data, steps=list(steps), code=code.strip("\n"), net=net)
