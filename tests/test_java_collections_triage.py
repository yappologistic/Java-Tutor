import unittest

from java_collections_triage_script import find_issue, issues, official_urls, render_text


class JavaCollectionsTriageTests(unittest.TestCase):
    def test_finds_hashcode_alias(self):
        issue = find_issue("hash map key")
        self.assertEqual(issue.key, "equals-hashcode")
        self.assertTrue(any("hashCode" in check for check in issue.first_checks))

    def test_finds_concurrent_modification_alias(self):
        issue = find_issue("modify while iterating")
        self.assertEqual(issue.key, "concurrent-modification")
        self.assertTrue(any("Iterator.remove" in fix for fix in issue.fixes_to_consider))

    def test_unknown_issue_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available issues"):
            find_issue("jdbc transaction")

    def test_render_text_contains_pitfalls_and_docs(self):
        text = render_text(find_issue("parallel stream"))
        self.assertIn("Pitfalls:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("parallel", text.lower())

    def test_official_urls_are_official_sources(self):
        urls = official_urls(issues())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/"), url)


if __name__ == "__main__":
    unittest.main()
