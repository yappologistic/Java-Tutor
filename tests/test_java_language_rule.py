import unittest

from java_language_rule_script import find_rule, official_urls, render_text, rules


class JavaLanguageRuleTests(unittest.TestCase):
    def test_finds_overload_alias(self):
        rule = find_rule("ambiguous method")
        self.assertEqual(rule.key, "overload-resolution")
        self.assertTrue(any("most-specific" in check for check in rule.first_checks))

    def test_finds_effectively_final_alias(self):
        rule = find_rule("effectively final")
        self.assertEqual(rule.key, "lambda-capture")
        self.assertTrue(any("captured local" in pitfall for pitfall in rule.common_pitfalls))

    def test_unknown_rule_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available rules"):
            find_rule("servlet lifecycle")

    def test_render_text_contains_pitfalls_and_docs(self):
        text = render_text(find_rule("try with resources"))
        self.assertIn("Common pitfalls:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("reverse order", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(rules())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith(("https://docs.oracle.com/", "https://openjdk.org/")), url)

    def test_api_and_language_links_honor_requested_version(self):
        try_with_resources = find_rule("try-with-resources", version="21")
        records = find_rule("records", version="21")
        self.assertIn(
            "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/AutoCloseable.html",
            try_with_resources.docs,
        )
        self.assertIn("https://docs.oracle.com/en/java/javase/21/language/records.html", records.docs)
        self.assertFalse(any("/java/javase/25/" in url for url in try_with_resources.docs + records.docs))


if __name__ == "__main__":
    unittest.main()
