"""Beginner lessons, one module per course tab. Importing this package registers them in lesson_util.LESSONS."""
import importlib, pkgutil, os
for _m in sorted(pkgutil.iter_modules([os.path.dirname(__file__)])):
    importlib.import_module(__name__ + "." + _m.name)
