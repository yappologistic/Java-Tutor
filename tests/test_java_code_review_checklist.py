import unittest

from java_code_review_checklist_script import checklist_payload, official_urls, render_text, select_areas


class JavaCodeReviewChecklistTests(unittest.TestCase):
    def test_default_checklist_includes_core_review_areas(self):
        payload = checklist_payload()
        keys = [area["key"] for area in payload["areas"]]
        self.assertIn("correctness", keys)
        self.assertIn("security", keys)
        self.assertIn("concurrency", keys)

    def test_focus_aliases_select_unique_areas(self):
        areas = select_areas(["threads", "concurrency", "secure"])
        self.assertEqual([area.key for area in areas], ["concurrency", "security"])

    def test_unknown_focus_raises_helpful_error(self):
        with self.assertRaisesRegex(ValueError, "unknown focus"):
            select_areas(["swing"])

    def test_official_urls_are_oracle_or_openjdk_docs(self):
        urls = official_urls(select_areas(["security", "concurrency"]))
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(
                url.startswith("https://docs.oracle.com/")
                or url.startswith("https://www.oracle.com/java/technologies/javase/")
                or url.startswith("https://openjdk.org/")
            )

    def test_render_text_has_docs_footer(self):
        text = render_text(["resources"])
        self.assertIn("Resource Management", text)
        self.assertIn("Official docs:", text)
        self.assertIn("AutoCloseable", text)

    def test_security_and_migration_docs_honor_requested_version(self):
        urls = official_urls(select_areas(["security", "compatibility"], version="21"))
        self.assertTrue(any("/java/javase/21/security/" in url for url in urls), urls)
        self.assertIn("https://docs.oracle.com/en/java/javase/21/migrate/index.html", urls)
        self.assertFalse(any("/java/javase/25/security/" in url or "/java/javase/25/migrate/" in url for url in urls))


if __name__ == "__main__":
    unittest.main()
