import unittest

from java_io_triage_script import find_issue, issues, official_urls, render_text


class JavaIoTriageTests(unittest.TestCase):
    def test_finds_charset_alias(self):
        issue = find_issue("utf-8")
        self.assertEqual(issue.key, "charset-text")
        self.assertTrue(any("charset" in check.lower() for check in issue.first_checks))

    def test_finds_resource_alias(self):
        issue = find_issue("try with resources")
        self.assertEqual(issue.key, "resource-lifecycle")
        self.assertTrue(any("AutoCloseable" in fix for fix in issue.fixes_to_consider))

    def test_unknown_issue_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available issues"):
            find_issue("jdbc pool")

    def test_render_text_contains_pitfalls_and_docs(self):
        text = render_text(find_issue("socket timeout"))
        self.assertIn("Pitfalls:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("timeout", text.lower())

    def test_official_urls_are_official_sources(self):
        urls = official_urls(issues())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith(("https://docs.oracle.com/", "https://www.oracle.com/java/")), url)


if __name__ == "__main__":
    unittest.main()
