import importlib.util
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "java-tutor" / "scripts" / "java_topic_links.py"
spec = importlib.util.spec_from_file_location("java_topic_links", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)

TOPICS = module.TOPICS
find_topic = module.find_topic
render_text = module.render_text
