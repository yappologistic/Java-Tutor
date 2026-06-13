import importlib.util
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "java-tutor" / "scripts" / "java_datetime_triage.py"
SPEC = importlib.util.spec_from_file_location("java_datetime_triage", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

DateTimeIssue = MODULE.DateTimeIssue
find_issue = MODULE.find_issue
issues = MODULE.issues
official_urls = MODULE.official_urls
render_text = MODULE.render_text
