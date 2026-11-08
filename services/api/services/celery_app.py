from __future__ import annotations

import os
import sys
from pathlib import Path

_root_services = Path(__file__).resolve().parent.parent.parent
_celery_path = _root_services / "celery_app.py"

if _celery_path.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("root_celery_app", _celery_path)
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        celery_app = getattr(mod, "celery_app", None)
    else:
        from celery import Celery
        celery_app = Celery("trackflow")
else:
    from celery import Celery
    celery_app = Celery("trackflow")

