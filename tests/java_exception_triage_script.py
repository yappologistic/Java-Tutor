import importlib.util
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "java-tutor" / "scripts" / "java_exception_triage.py"
spec = importlib.util.spec_from_file_location("java_exception_triage", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)

EXCEPTIONS = module.EXCEPTIONS
api_link = module.api_link
extract_exception_name = module.extract_exception_name
render_text = module.render_text
triage = module.triage
