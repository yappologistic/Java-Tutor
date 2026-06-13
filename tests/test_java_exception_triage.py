import unittest

from java_exception_triage_script import EXCEPTIONS, api_link, extract_exception_name, render_text, triage


class JavaExceptionTriageTests(unittest.TestCase):
    def test_extracts_exception_from_stack_trace_line(self):
        text = 'Exception in thread "main" java.lang.NullPointerException: boom'
        self.assertEqual(extract_exception_name(text), "NullPointerException")

    def test_triages_null_pointer_exception(self):
        item = triage("java.lang.NullPointerException")
        self.assertEqual(item.api_class, "java.lang.NullPointerException")
        self.assertTrue(any("unexpected null" in check for check in item.first_checks))

    def test_api_link_uses_official_oracle_docs(self):
        self.assertEqual(
            api_link("java.util.ConcurrentModificationException", "25"),
            "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/ConcurrentModificationException.html",
        )

    def test_every_exception_has_first_checks(self):
        for item in EXCEPTIONS:
            self.assertGreaterEqual(len(item.first_checks), 3, item.name)

    def test_render_text_has_official_docs_footer(self):
        text = render_text(triage("NumberFormatException"), "25")
        self.assertIn("Official docs:", text)
        self.assertIn("NumberFormatException.html", text)

    def test_unknown_exception_is_rejected(self):
        with self.assertRaises(ValueError):
            triage("MadeUpException")


if __name__ == "__main__":
    unittest.main()
