import unittest

from java_jvm_option_script import areas, find_area, official_urls, render_text


class JavaJvmOptionTests(unittest.TestCase):
    def test_finds_xmx_alias(self):
        area = find_area("xmx")
        self.assertEqual(area.key, "heap-sizing")
        self.assertIn("-Xmx", area.option_families)

    def test_finds_preview_alias(self):
        area = find_area("enable-preview")
        self.assertEqual(area.key, "preview-features")
        self.assertTrue(any("--enable-preview" in option for option in area.option_families))

    def test_unknown_area_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available areas"):
            find_area("maven surefire")

    def test_render_text_contains_cautions_and_docs(self):
        text = render_text(find_area("module-access"))
        self.assertIn("Cautions:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("--add-opens", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(areas())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith(("https://docs.oracle.com/", "https://openjdk.org/")), url)


if __name__ == "__main__":
    unittest.main()
