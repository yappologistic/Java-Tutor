import unittest

from java_annotations_triage_script import find_issue, issues, official_urls, render_text


class JavaAnnotationsTriageTests(unittest.TestCase):
    def test_finds_retention_alias(self):
        issue = find_issue("runtime annotation")
        self.assertEqual(issue.key, "retention-target")
        self.assertTrue(any("RetentionPolicy.RUNTIME" in fix for fix in issue.fixes_to_consider))

    def test_finds_processor_alias(self):
        issue = find_issue("annotation processor")
        self.assertEqual(issue.key, "annotation-processing")
        self.assertTrue(any("Filer" in check or "Messager" in check for check in issue.first_checks))

    def test_finds_type_use_alias(self):
        issue = find_issue("receiver annotation")
        self.assertEqual(issue.key, "type-use")
        self.assertTrue(any("TYPE_USE" in check for check in issue.first_checks))

    def test_unknown_issue_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available issues"):
            find_issue("jdbc connection pool")

    def test_render_text_contains_pitfalls_and_docs(self):
        text = render_text(find_issue("repeatable annotation"))
        self.assertIn("Pitfalls:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("@Repeatable", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(issues())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/"), url)


if __name__ == "__main__":
    unittest.main()
