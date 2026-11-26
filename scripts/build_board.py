import json, datetime
from plan_data import as_json
TAUGHT = [1, 2]
t = open("board_template.html").read()
PJ = as_json().replace("</", "<\\/")  # keep "</script" inside JSON strings from closing the page script
t = t.replace("__PLAN__", PJ).replace("__TAUGHT__", json.dumps(TAUGHT)).replace("__UPDATED__", json.dumps(datetime.date.today().strftime("%d %b %Y")))
t = t.replace("/*__SDCSS__*/", open("sd/sd_ui.css").read() + "\n" + open("ml/ml_ui.css").read()).replace("/*__SDJS__*/", open("sd/sd_ui.js").read() + "\n" + open("ml/ml_ui.js").read() + "\n" + open("ml/ml_demos.js").read() + "\n" + open("sd/sd_notes.js").read() + "\n" + open("sd/sd_abbr.js").read() + "\n" + open("sd/sd_explain.js").read() + "\n" + open("sd/sd_viz.js").read() + "\n" + open("sd/sd_highlight.js").read())
assert "</script" not in PJ.lower()
import hashlib
t = t.replace("__BUILD__", hashlib.sha1(t.encode()).hexdigest()[:12])
open("dsa-sticky-notes.html","w").write(t)
