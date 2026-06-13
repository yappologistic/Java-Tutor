import unittest

from java_feature_compat_script import compatibility, parse_major, render_text


class JavaFeatureCompatTests(unittest.TestCase):
    def test_parse_major_supports_legacy_version_format(self):
        self.assertEqual(parse_major("1.8"), 8)
        self.assertEqual(parse_major("21.0.2"), 21)

    def test_records_unavailable_on_java_11(self):
        result = compatibility("records", "11")
        self.assertFalse(result["available"])
        self.assertEqual(result["minimum_version"], "16")
        self.assertEqual(result["documentation_version"], "16")
        self.assertIn("requires Java 16", result["recommendation"])
        self.assertTrue(any("/java/javase/16/" in link for link in result["official_docs"]))

    def test_virtual_threads_available_on_java_21(self):
        result = compatibility("loom", "21")
        self.assertTrue(result["available"])
        self.assertEqual(result["topic"]["key"], "virtual-threads")
        self.assertEqual(result["documentation_version"], "21")
        self.assertTrue(any("/java/javase/21/" in link for link in result["official_docs"]))

    def test_sequenced_collections_require_java_21(self):
        result = compatibility("sequenced collection", "17")
        self.assertFalse(result["available"])
        self.assertEqual(result["minimum_version"], "21")
        self.assertEqual(result["documentation_version"], "21")
        self.assertIn("requires Java 21", result["recommendation"])

    def test_unavailable_virtual_threads_use_minimum_version_docs(self):
        result = compatibility("virtual-threads", "20")
        self.assertFalse(result["available"])
        self.assertEqual(result["documentation_version"], "21")
        self.assertFalse(any("/java/javase/20/" in link for link in result["official_docs"]))
        self.assertTrue(any("/java/javase/21/" in link for link in result["official_docs"]))

    def test_unknown_version_rejected(self):
        with self.assertRaisesRegex(ValueError, "could not parse"):
            compatibility("streams", "lts")

    def test_render_text_includes_docs(self):
        text = render_text(compatibility("switch expressions", "17"))
        self.assertIn("Compatibility: Available", text)
        self.assertIn("Official docs:", text)
        self.assertIn("openjdk.org/jeps/361", text)


if __name__ == "__main__":
    unittest.main()
