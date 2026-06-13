import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_project.py"
spec = importlib.util.spec_from_file_location("verify_project", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

OFFICIAL_URLS = module.OFFICIAL_URLS
RELEASE_FACT_CHECKS = module.RELEASE_FACT_CHECKS
checked_url_status = module.checked_url_status
normalize_text = module.normalize_text
parse_frontmatter = module.parse_frontmatter
topic_urls = module.topic_urls
