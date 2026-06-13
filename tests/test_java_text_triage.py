import unittest

from java_text_triage_script import find_issue, issues, official_urls, render_text


class JavaTextTriageTests(unittest.TestCase):
    def test_finds_turkish_i_alias(self):
        issue = find_issue("turkish i")
        self.assertEqual(issue.key, "locale-case")
        self.assertTrue(any("Locale.ROOT" in fix for fix in issue.fixes_to_consider))

    def test_finds_emoji_alias(self):
        issue = find_issue("emoji")
        self.assertEqual(issue.key, "unicode-codepoints")
        self.assertTrue(any("code point" in check.lower() for check in issue.first_checks))

    def test_finds_charset_alias(self):
        issue = find_issue("mojibake")
        self.assertEqual(issue.key, "charset-boundary")
        self.assertTrue(any("StandardCharsets.UTF_8" in fix for fix in issue.fixes_to_consider))

    def test_unknown_issue_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available issues"):
            find_issue("jdbc connection pool")

    def test_render_text_contains_pitfalls_and_docs(self):
        text = render_text(find_issue("text block"))
        self.assertIn("Pitfalls:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("Text blocks", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(issues())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/"), url)


if __name__ == "__main__":
    unittest.main()
