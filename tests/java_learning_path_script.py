import importlib.util
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "java-tutor" / "scripts" / "java_learning_path.py"
spec = importlib.util.spec_from_file_location("java_learning_path", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)

build_path = module.build_path
official_urls = module.official_urls
render_text = module.render_text
