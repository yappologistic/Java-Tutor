import unittest

from java_regex_triage_script import find_issue, issues, official_urls, render_text


class JavaRegexTriageTests(unittest.TestCase):
    def test_finds_matches_alias(self):
        issue = find_issue("string matches")
        self.assertEqual(issue.key, "matches-vs-find")
        self.assertTrue(any("full" in check.lower() for check in issue.first_checks))

    def test_finds_replacement_alias(self):
        issue = find_issue("quote replacement")
        self.assertEqual(issue.key, "replacement-quoting")
        self.assertTrue(any("quoteReplacement" in fix for fix in issue.fixes_to_consider))

    def test_unknown_issue_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available issues"):
            find_issue("jdbc connection pool")

    def test_render_text_contains_pitfalls_and_docs(self):
        text = render_text(find_issue("backtracking"))
        self.assertIn("Pitfalls:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("Pattern", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(issues())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/"), url)

    def test_no_known_bad_pattern_summary_fragment(self):
        urls = official_urls(issues())
        self.assertFalse(any(url.endswith("Pattern.html#sum") for url in urls), urls)


if __name__ == "__main__":
    unittest.main()
