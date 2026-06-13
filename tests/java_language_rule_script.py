import importlib.util
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "java-tutor" / "scripts" / "java_language_rule.py"
spec = importlib.util.spec_from_file_location("java_language_rule", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)

find_rule = module.find_rule
official_urls = module.official_urls
render_text = module.render_text
rules = module.rules
