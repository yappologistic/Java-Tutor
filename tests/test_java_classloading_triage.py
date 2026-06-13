import unittest

from java_classloading_triage_script import find_issue, issues, official_urls, render_text


class JavaClassLoadingTriageTests(unittest.TestCase):
    def test_finds_no_class_def_alias(self):
        issue = find_issue("noclassdeffounderror")
        self.assertEqual(issue.key, "not-found")
        self.assertTrue(any("runtime" in check.lower() for check in issue.first_checks))

    def test_finds_service_loader_alias(self):
        issue = find_issue("META-INF/services")
        self.assertEqual(issue.key, "services")
        self.assertTrue(any("ServiceLoader" in fix for fix in issue.fixes_to_consider))

    def test_unknown_issue_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available issues"):
            find_issue("jdbc connection pool")

    def test_render_text_contains_pitfalls_and_docs(self):
        text = render_text(find_issue("duplicate class"))
        self.assertIn("Pitfalls:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("ClassLoader", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(issues())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/"), url)


if __name__ == "__main__":
    unittest.main()
