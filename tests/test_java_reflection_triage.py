import unittest

from java_reflection_triage_script import find_issue, issues, official_urls, render_text


class JavaReflectionTriageTests(unittest.TestCase):
    def test_finds_retention_alias(self):
        issue = find_issue("runtime annotation")
        self.assertEqual(issue.key, "annotations-retention")
        self.assertTrue(any("RetentionPolicy.RUNTIME" in fix for fix in issue.fixes_to_consider))

    def test_finds_module_alias(self):
        issue = find_issue("add-opens")
        self.assertEqual(issue.key, "modules-opens")
        self.assertTrue(any("opens" in pitfall.lower() for pitfall in issue.pitfalls))

    def test_unknown_issue_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available issues"):
            find_issue("jdbc connection pool")

    def test_render_text_contains_pitfalls_and_docs(self):
        text = render_text(find_issue("methodhandle"))
        self.assertIn("Pitfalls:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("MethodHandle", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(issues())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/"), url)


if __name__ == "__main__":
    unittest.main()
