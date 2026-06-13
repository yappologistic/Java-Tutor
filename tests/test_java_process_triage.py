import unittest

from java_process_triage_script import find_issue, issues, official_urls, render_text


class JavaProcessTriageTests(unittest.TestCase):
    def test_finds_runtime_exec_alias(self):
        issue = find_issue("runtime exec")
        self.assertEqual(issue.key, "command-arguments")
        self.assertTrue(any("separate list elements" in fix for fix in issue.fixes_to_consider))

    def test_finds_pipe_deadlock_alias(self):
        issue = find_issue("deadlock")
        self.assertEqual(issue.key, "stdio-deadlock")
        self.assertTrue(any("waitFor" in pitfall for pitfall in issue.pitfalls))

    def test_unknown_issue_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available issues"):
            find_issue("jdbc connection pool")

    def test_render_text_contains_pitfalls_and_docs(self):
        text = render_text(find_issue("timeout"))
        self.assertIn("Pitfalls:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("Process", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(issues())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/"), url)


if __name__ == "__main__":
    unittest.main()
