"""Run every real-data walkthrough generator and write walks.json (read by ml_data.py).
usage: python3 generate_walks.py [w_module ...]   (no args = all)"""
import importlib, json, os, sys, time, warnings
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import walk_util
mods = sys.argv[1:] or sorted(f[:-3] for f in os.listdir(os.path.join(HERE, "walks")) if f.startswith("w_"))
for m in mods: importlib.import_module("walks." + m)
path = os.path.join(HERE, "walks.json")
old = json.load(open(path)) if os.path.exists(path) and sys.argv[1:] else {}
t0 = time.time(); new = walk_util.build_all({'walks.' + m for m in sys.argv[1:]} or None)
old.update(new)
json.dump(old, open(path, "w"), indent=0, ensure_ascii=False)
print(f"{len(new)} walkthroughs built in {time.time() - t0:.0f}s; walks.json has {len(old)}")
