import unittest

from java_http_triage_script import find_issue, issues, official_urls, render_text


class JavaHttpTriageTests(unittest.TestCase):
    def test_finds_timeout_alias(self):
        issue = find_issue("httptimeoutexception")
        self.assertEqual(issue.key, "timeouts-redirects")
        self.assertTrue(any("timeout" in check.lower() for check in issue.first_checks))

    def test_finds_tls_alias(self):
        issue = find_issue("certificate")
        self.assertEqual(issue.key, "proxy-tls-auth")
        self.assertTrue(any("SSLContext" in fix for fix in issue.fixes_to_consider))

    def test_unknown_issue_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available issues"):
            find_issue("jdbc connection pool")

    def test_render_text_contains_pitfalls_and_docs(self):
        text = render_text(find_issue("websocket"))
        self.assertIn("Pitfalls:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("WebSocket", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(issues())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/"), url)


if __name__ == "__main__":
    unittest.main()
