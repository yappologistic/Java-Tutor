import unittest

from java_compile_error_triage_script import detect, diagnostics, official_urls, render_text, select


class JavaCompileErrorTriageTests(unittest.TestCase):
    def test_detects_cannot_find_symbol(self):
        item = detect("error: cannot find symbol\n  symbol: class Widget")
        self.assertEqual(item.key, "cannot-find-symbol")
        self.assertIn("class path", item.summary)

    def test_detects_release_mismatch(self):
        item = detect("error: release version 25 not supported")
        self.assertEqual(item.key, "release-source-target")

    def test_select_rejects_unknown_key(self):
        with self.assertRaisesRegex(ValueError, "unknown diagnostic key"):
            select("unknown")

    def test_render_text_has_first_checks_and_docs(self):
        text = render_text(select("definite-assignment"))
        self.assertIn("First checks:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("jls-16", text)

    def test_official_urls_are_oracle_docs(self):
        urls = official_urls(diagnostics())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/"))


if __name__ == "__main__":
    unittest.main()
