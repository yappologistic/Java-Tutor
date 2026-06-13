import unittest

from java_migration_plan_script import build_plan, render_text


class JavaMigrationPlanTests(unittest.TestCase):
    def test_builds_java_8_to_25_plan(self):
        plan = build_plan("8", "25")
        self.assertEqual(plan.source, "8")
        self.assertEqual(plan.target, "25")
        self.assertIn("https://docs.oracle.com/en/java/javase/25/migrate/index.html", plan.official_docs)
        self.assertTrue(any("Java EE and CORBA" in check for check in plan.checks))
        self.assertTrue(any("current LTS baseline" in check for check in plan.checks))

    def test_normalizes_legacy_source_version(self):
        plan = build_plan("1.8", "21")
        self.assertEqual(plan.source, "8")

    def test_rejects_downgrade(self):
        with self.assertRaises(ValueError):
            build_plan("21", "17")

    def test_render_text_has_official_docs_footer(self):
        text = render_text(build_plan("17", "21"))
        self.assertIn("Official docs:", text)
        self.assertIn("https://docs.oracle.com/en/java/javase/21/migrate/index.html", text)


if __name__ == "__main__":
    unittest.main()
