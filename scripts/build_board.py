import json, datetime
from plan_data import as_json
TAUGHT = [1]
t = open("board_template.html").read()
t = t.replace("__PLAN__", as_json()).replace("__TAUGHT__", json.dumps(TAUGHT)).replace("__UPDATED__", json.dumps(datetime.date.today().strftime("%d %b %Y")))
open("dsa-sticky-notes.html","w").write(t)
