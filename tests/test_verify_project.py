import unittest

from verify_project_script import OFFICIAL_URLS, parse_frontmatter


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


if __name__ == "__main__":
    unittest.main()
