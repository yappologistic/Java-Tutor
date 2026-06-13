import unittest

from java_concurrency_triage_script import concerns, find_concern, official_urls, render_text


class JavaConcurrencyTriageTests(unittest.TestCase):
    def test_finds_stale_read_alias(self):
        concern = find_concern("stale read")
        self.assertEqual(concern.key, "data-race")
        self.assertTrue(any("happens-before" in check for check in concern.first_checks))

    def test_finds_interrupt_alias(self):
        concern = find_concern("interrupt")
        self.assertEqual(concern.key, "interruption-cancellation")
        self.assertTrue(any("InterruptedException" in check for check in concern.first_checks))

    def test_unknown_concern_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available concerns"):
            find_concern("servlet")

    def test_render_text_contains_evidence_safer_defaults_and_docs(self):
        text = render_text(find_concern("executor"))
        self.assertIn("Evidence to collect:", text)
        self.assertIn("Safer defaults:", text)
        self.assertIn("Official docs:", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(concerns())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/"))

    def test_jls_memory_model_link_honors_requested_version(self):
        concern = find_concern("data-race", version="21")
        self.assertTrue(any("/jls/se21/" in url for url in concern.docs), concern.docs)
        self.assertFalse(any("/jls/se25/" in url for url in concern.docs), concern.docs)


if __name__ == "__main__":
    unittest.main()
