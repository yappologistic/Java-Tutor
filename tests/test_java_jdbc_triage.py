import unittest

from java_jdbc_triage_script import find_issue, issues, official_urls, render_text


class JavaJdbcTriageTests(unittest.TestCase):
    def test_finds_prepared_statement_alias(self):
        issue = find_issue("sql injection")
        self.assertEqual(issue.key, "prepared-statements")
        self.assertTrue(any("PreparedStatement" in fix for fix in issue.fixes_to_consider))

    def test_finds_transaction_alias(self):
        issue = find_issue("rollback")
        self.assertEqual(issue.key, "transactions")
        self.assertTrue(any("auto-commit" in check.lower() for check in issue.first_checks))

    def test_unknown_issue_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available issues"):
            find_issue("regex backtracking")

    def test_render_text_contains_pitfalls_and_docs(self):
        text = render_text(find_issue("timestamp"))
        self.assertIn("Pitfalls:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("Timestamp", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(issues())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/"), url)


if __name__ == "__main__":
    unittest.main()
