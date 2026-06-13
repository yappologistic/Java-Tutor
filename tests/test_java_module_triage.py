import unittest

from java_module_triage_script import find_issue, issues, official_urls, render_text


class JavaModuleTriageTests(unittest.TestCase):
    def test_finds_add_opens_alias(self):
        issue = find_issue("add-opens")
        self.assertEqual(issue.key, "exports-opens")
        self.assertTrue(any("reflection" in check.lower() for check in issue.first_checks))

    def test_finds_split_package_alias(self):
        issue = find_issue("package exists in another module")
        self.assertEqual(issue.key, "split-packages")
        self.assertTrue(any("duplicate" in item.lower() for item in issue.fixes_to_consider))

    def test_unknown_issue_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available issues"):
            find_issue("servlet container")

    def test_render_text_contains_fixes_cautions_and_docs(self):
        text = render_text(find_issue("serviceloader"))
        self.assertIn("Fixes to consider:", text)
        self.assertIn("Cautions:", text)
        self.assertIn("Official docs:", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(issues())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith(("https://docs.oracle.com/", "https://openjdk.org/")), url)


if __name__ == "__main__":
    unittest.main()
