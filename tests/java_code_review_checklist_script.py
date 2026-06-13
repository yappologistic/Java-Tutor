import importlib.util
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "java-tutor" / "scripts" / "java_code_review_checklist.py"
spec = importlib.util.spec_from_file_location("java_code_review_checklist", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)

checklist_payload = module.checklist_payload
official_urls = module.official_urls
render_text = module.render_text
select_areas = module.select_areas
