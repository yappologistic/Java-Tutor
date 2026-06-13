import unittest

from java_performance_triage_script import find_symptom, official_urls, render_text, symptoms


class JavaPerformanceTriageTests(unittest.TestCase):
    def test_finds_gc_alias(self):
        symptom = find_symptom("garbage collection")
        self.assertEqual(symptom.key, "gc-pauses")
        self.assertIn("GC logs", symptom.evidence[0])

    def test_finds_memory_leak_alias(self):
        symptom = find_symptom("outofmemory")
        self.assertEqual(symptom.key, "memory-leak")
        self.assertTrue(any("heap" in command.lower() for command in symptom.commands))

    def test_unknown_symptom_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available symptoms"):
            find_symptom("graphics")

    def test_render_text_contains_commands_and_docs(self):
        text = render_text(find_symptom("high-cpu"))
        self.assertIn("Useful commands:", text)
        self.assertIn("jcmd", text)
        self.assertIn("Official docs:", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(symptoms())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/") or url.startswith("https://dev.java/"))


if __name__ == "__main__":
    unittest.main()
