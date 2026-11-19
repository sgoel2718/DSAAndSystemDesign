LEVELS = ("Basic", "Intermediate", "Advanced")


def C(id, title, level, what, body, analogy="", example="", tips=(), diagram=None, lab=None, see=()):
    assert level in LEVELS, (id, level)
    return dict(id=id, title=title, level=level, what=what, body=body.strip(), analogy=analogy, example=example,
                tips=list(tips), diagram=diagram, lab=lab, see=list(see))
