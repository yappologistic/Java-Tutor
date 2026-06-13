import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "java-tutor" / "scripts" / "java_doc_link.py"
spec = importlib.util.spec_from_file_location("java_doc_link", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

build_link = module.build_link
