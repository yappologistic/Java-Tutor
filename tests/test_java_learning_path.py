import unittest

from java_learning_path_script import build_path, official_urls, render_text


class JavaLearningPathTests(unittest.TestCase):
    def test_beginner_path_has_fundamentals(self):
        path = build_path("beginner")
        titles = [step.title for step in path.steps]
        self.assertIn("Set up, compile, and run Java", titles)
        self.assertGreaterEqual(len(path.steps), 4)

    def test_level_alias_maps_to_professional(self):
        path = build_path("senior", "concurrency")
        self.assertEqual(path.level, "professional")
        self.assertEqual(len(path.steps), 1)
        self.assertIn("concurrent", path.steps[0].title.lower())

    def test_goal_without_match_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "did not match"):
            build_path("beginner", "security")

    def test_render_text_includes_official_docs_footer(self):
        text = render_text(build_path("intermediate", "streams"))
        self.assertIn("Java learning path: intermediate", text)
        self.assertIn("Official docs:", text)
        self.assertIn("dev.java/learn/api/streams", text)

    def test_official_urls_are_official_java_sources(self):
        urls = official_urls(build_path("professional"))
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(
                url.startswith("https://docs.oracle.com/")
                or url.startswith("https://www.oracle.com/java/technologies/")
                or url.startswith("https://openjdk.org/")
            )


if __name__ == "__main__":
    unittest.main()
