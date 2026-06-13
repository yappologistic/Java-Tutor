import unittest

from java_datetime_triage_script import find_issue, issues, official_urls, render_text


class JavaDateTimeTriageTests(unittest.TestCase):
    def test_finds_dst_alias(self):
        issue = find_issue("dst")
        self.assertEqual(issue.key, "time-zones")
        self.assertTrue(any("gap" in check.lower() or "overlap" in check.lower() for check in issue.first_checks))

    def test_finds_legacy_formatter_alias(self):
        issue = find_issue("simpledateformat")
        self.assertEqual(issue.key, "legacy-interop")
        self.assertTrue(any("thread" in pitfall.lower() for pitfall in issue.pitfalls))

    def test_unknown_issue_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available issues"):
            find_issue("jdbc connection pool")

    def test_render_text_contains_pitfalls_and_docs(self):
        text = render_text(find_issue("offset"))
        self.assertIn("Pitfalls:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("OffsetDateTime", text)

    def test_official_urls_are_oracle_docs(self):
        urls = official_urls(issues())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/"), url)


if __name__ == "__main__":
    unittest.main()
