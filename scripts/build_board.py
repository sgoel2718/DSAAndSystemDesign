import json, datetime
from plan_data import as_json
TAUGHT = [1, 2]
t = open("board_template.html").read()
t = t.replace("__PLAN__", as_json()).replace("__TAUGHT__", json.dumps(TAUGHT)).replace("__UPDATED__", json.dumps(datetime.date.today().strftime("%d %b %Y")))
t = t.replace("/*__SDCSS__*/", open("sd/sd_ui.css").read()).replace("/*__SDJS__*/", open("sd/sd_ui.js").read())
assert "</script" not in as_json().lower()
open("dsa-sticky-notes.html","w").write(t)
