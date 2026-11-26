"""Registry for the runnable Java practice programs shown on System Design concept and HLD cards."""
import re
JAVA = {}


def J(id, code, tasks):
    code = code.strip("\n") + "\n"
    cls = re.search(r"public class (\w+)", code).group(1)
    assert id not in JAVA, "duplicate java for " + id
    JAVA[id] = dict(code=code, tasks=list(tasks), cls=cls)
