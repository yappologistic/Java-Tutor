import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "java-tutor" / "scripts"


VALID_COMMANDS = {
    "java_annotations_triage.py": ["retention"],
    "java_classloading_triage.py": ["noclassdeffounderror"],
    "java_code_review_checklist.py": ["resources"],
    "java_collections_triage.py": ["hashcode"],
    "java_compile_error_triage.py": ["cannot find symbol"],
    "java_concurrency_triage.py": ["data-race"],
    "java_datetime_triage.py": ["dst"],
    "java_deprecation_audit.py": ["--target", "25"],
    "java_doc_link.py": ["api", "java.util.Map.Entry"],
    "java_exception_triage.py": ["NullPointerException"],
    "java_feature_compat.py": ["records", "--version", "21"],
    "java_generics_triage.py": ["pecs"],
    "java_http_triage.py": ["timeout"],
    "java_io_triage.py": ["utf-8"],
    "java_jdbc_triage.py": ["sql injection"],
    "java_jdk_tool.py": ["javac"],
    "java_jvm_option.py": ["xmx"],
    "java_language_rule.py": ["overload"],
    "java_learning_path.py": ["beginner"],
    "java_migration_plan.py": ["17", "25"],
    "java_module_triage.py": ["add-opens"],
    "java_numeric_triage.py": ["bigdecimal"],
    "java_performance_triage.py": ["gc"],
    "java_process_triage.py": ["timeout"],
    "java_project_info.py": ["."],
    "java_reflection_triage.py": ["retention"],
    "java_regex_triage.py": ["backtracking"],
    "java_security_triage.py": ["deserialization"],
    "java_text_triage.py": ["mojibake"],
    "java_topic_links.py": ["records"],
    "java_verify_commands.py": ["."],
    "java_version_consistency.py": ["."],
}


def run_script(script_name, args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script_name), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=20,
    )


class CliSmokeTests(unittest.TestCase):
    def test_every_script_has_help(self):
        for script_name in VALID_COMMANDS:
            with self.subTest(script=script_name):
                result = run_script(script_name, ["--help"])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout)

    def test_every_script_rejects_unknown_options(self):
        for script_name in VALID_COMMANDS:
            with self.subTest(script=script_name):
                result = run_script(script_name, ["--definitely-invalid-option"])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("usage:", result.stderr)

    def test_every_script_accepts_representative_valid_command(self):
        for script_name, args in VALID_COMMANDS.items():
            with self.subTest(script=script_name):
                result = run_script(script_name, args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout.strip())

    def test_json_output_where_supported_is_parseable(self):
        for script_name, args in VALID_COMMANDS.items():
            help_result = run_script(script_name, ["--help"])
            if "--json" not in help_result.stdout:
                continue
            with self.subTest(script=script_name):
                result = run_script(script_name, [*args, "--json"])
                self.assertEqual(result.returncode, 0, result.stderr)
                json.loads(result.stdout)


if __name__ == "__main__":
    unittest.main()
