import unittest

from verify_project_script import (
    OFFICIAL_URLS,
    RELEASE_FACT_CHECKS,
    checked_url_status,
    normalize_text,
    parse_frontmatter,
    topic_urls,
)


class FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


class FlakyOpener:
    def __init__(self):
        self.calls = 0

    def open(self, request, timeout):
        self.calls += 1
        if self.calls == 1:
            raise TimeoutError("temporary timeout")
        return FakeResponse()


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
            "https://openjdk.org/",
        )
        for check in RELEASE_FACT_CHECKS:
            self.assertTrue(check["url"].startswith(allowed_hosts), check["url"])
            self.assertTrue(check["required"], check["name"])

    def test_topic_urls_are_resolved_before_link_checking(self):
        urls = list(topic_urls())
        self.assertTrue(urls)
        self.assertFalse(any("{version}" in url for url in urls), urls)

    def test_checked_url_status_retries_transient_timeout(self):
        opener = FlakyOpener()
        self.assertEqual(checked_url_status(opener, "https://docs.oracle.com/example"), 200)
        self.assertEqual(opener.calls, 2)


if __name__ == "__main__":
    unittest.main()
