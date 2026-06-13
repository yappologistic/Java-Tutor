import unittest

from java_numeric_triage_script import find_issue, issues, official_urls, render_text


class JavaNumericTriageTests(unittest.TestCase):
    def test_finds_bigdecimal_alias(self):
        issue = find_issue("money")
        self.assertEqual(issue.key, "bigdecimal-money")
        self.assertTrue(any("RoundingMode" in fix for fix in issue.fixes_to_consider))

    def test_finds_overflow_alias(self):
        issue = find_issue("addexact")
        self.assertEqual(issue.key, "overflow")
        self.assertTrue(any("wraps" in pitfall.lower() for pitfall in issue.pitfalls))

    def test_unknown_issue_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available issues"):
            find_issue("jdbc connection pool")

    def test_render_text_contains_pitfalls_and_docs(self):
        text = render_text(find_issue("integer division"))
        self.assertIn("Pitfalls:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("BigDecimal", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(issues())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith(("https://docs.oracle.com/",)), url)

    def test_jls_links_honor_requested_version(self):
        issue = find_issue("integer division", version="21")
        self.assertTrue(any("/jls/se21/" in url for url in issue.docs), issue.docs)
        self.assertFalse(any("/jls/se25/" in url for url in issue.docs), issue.docs)


if __name__ == "__main__":
    unittest.main()
