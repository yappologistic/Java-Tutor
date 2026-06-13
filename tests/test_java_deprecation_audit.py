import unittest

from java_deprecation_audit_script import build_plan, official_urls, render_text


class JavaDeprecationAuditTests(unittest.TestCase):
    def test_build_plan_includes_jdeprscan_and_jdeps(self):
        plan = build_plan("25", "target/app.jar")
        commands = "\n".join(plan.commands)
        self.assertIn("jdeprscan --release 25 target/app.jar", commands)
        self.assertIn("jdeps --jdk-internals --multi-release 25 target/app.jar", commands)

    def test_legacy_target_is_normalized(self):
        plan = build_plan("1.11", "out")
        self.assertEqual(plan.target, "11")

    def test_unsupported_target_rejected(self):
        with self.assertRaisesRegex(ValueError, "supported target"):
            build_plan("19")

    def test_official_urls_reject_unsupported_target(self):
        with self.assertRaisesRegex(ValueError, "supported target"):
            official_urls("24")

    def test_render_text_contains_limitations_and_docs(self):
        text = render_text(build_plan("21"))
        self.assertIn("Limitations:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("jdeprscan", text)

    def test_official_urls_are_oracle_sources(self):
        urls = official_urls("25")
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/") or url.startswith("https://www.oracle.com/"))


if __name__ == "__main__":
    unittest.main()
