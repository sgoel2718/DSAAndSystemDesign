LEVELS = ("Basic", "Intermediate", "Advanced")


def H(id, title, level, companies, tests, functional, nonfunctional, estimates, api, data, design, flow, deep, tradeoffs=(), followups=()):
    """One high-level design interview question with a complete model answer."""
    assert level in LEVELS, (id, level)
    return dict(id=id, title=title, level=level, companies=list(companies), tests=tests, functional=list(functional),
                nonfunctional=list(nonfunctional), estimates=estimates.strip(), api=api.strip(), data=data.strip(),
                design=design, flow=list(flow), deep=list(deep), tradeoffs=list(tradeoffs), followups=list(followups))


def L(id, title, level, companies, requirements, entities, patterns, code, extensions=()):
    """One low-level design (machine coding) question with Java code."""
    assert level in LEVELS, (id, level)
    return dict(id=id, title=title, level=level, companies=list(companies), requirements=list(requirements),
                entities=list(entities), patterns=list(patterns), code=code.strip("\n"), extensions=list(extensions))


def Q(level, topic, q, a):
    assert level in LEVELS, (q, level)
    return dict(level=level, topic=topic, q=q, a=a.strip())
