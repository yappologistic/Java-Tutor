import unittest

from verify_project_script import OFFICIAL_URLS, RELEASE_FACT_CHECKS, normalize_text, parse_frontmatter


class VerifyProjectTests(unittest.TestCase):
    def test_parse_frontmatter(self):
        fields = parse_frontmatter("---\nname: java-tutor\ndescription: Example\n---\n# Body\n")
        self.assertEqual(fields["name"], "java-tutor")
        self.assertEqual(fields["description"], "Example")

    def test_official_urls_are_official_sources(self):
        allowed_hosts = (
            "https://docs.oracle.com/",
            "https://www.oracle.com/",
            "https://openjdk.org/",
            "https://dev.java/",
        )
        for url in OFFICIAL_URLS:
            self.assertTrue(url.startswith(allowed_hosts), url)

    def test_normalize_text_strips_markup_and_whitespace(self):
        self.assertEqual(normalize_text("<p>JDK&nbsp;25</p>\n  is LTS"), "JDK 25 is LTS")

    def test_release_fact_checks_use_official_sources(self):
        allowed_hosts = (
            "https://docs.oracle.com/",
            "https://www.oracle.com/",
        )
        for check in RELEASE_FACT_CHECKS:
            self.assertTrue(check["url"].startswith(allowed_hosts), check["url"])
            self.assertTrue(check["required"], check["name"])


if __name__ == "__main__":
    unittest.main()
