import unittest

from java_generics_triage_script import find_issue, issues, official_urls, render_text


class JavaGenericsTriageTests(unittest.TestCase):
    def test_finds_wildcard_alias(self):
        issue = find_issue("pecs")
        self.assertEqual(issue.key, "invariance-wildcards")
        self.assertTrue(any("? extends T" in fix for fix in issue.fixes_to_consider))

    def test_finds_heap_pollution_alias(self):
        issue = find_issue("heap pollution")
        self.assertEqual(issue.key, "raw-unchecked")
        self.assertTrue(any("unchecked" in check.lower() for check in issue.first_checks))

    def test_finds_bridge_alias(self):
        issue = find_issue("same erasure")
        self.assertEqual(issue.key, "bridge-erasure-clash")
        self.assertTrue(any("erased" in check.lower() for check in issue.first_checks))

    def test_unknown_issue_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available issues"):
            find_issue("jdbc transaction")

    def test_render_text_contains_pitfalls_and_docs(self):
        text = render_text(find_issue("cannot infer type"))
        self.assertIn("Pitfalls:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("type inference", text.lower())

    def test_official_urls_are_official_sources(self):
        urls = official_urls(issues())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/"), url)


if __name__ == "__main__":
    unittest.main()
