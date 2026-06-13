import importlib.util
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "java-tutor" / "scripts" / "java_deprecation_audit.py"
spec = importlib.util.spec_from_file_location("java_deprecation_audit", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)

build_plan = module.build_plan
official_urls = module.official_urls
render_text = module.render_text
