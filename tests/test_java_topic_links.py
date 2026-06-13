import unittest

from java_topic_links_script import TOPICS, find_topic, render_text


class JavaTopicLinksTests(unittest.TestCase):
    def test_finds_topic_by_key(self):
        topic = find_topic("virtual-threads")
        self.assertEqual(topic.minimum_version, "21")
        self.assertIn("https://openjdk.org/jeps/444", topic.links)

    def test_finds_topic_by_alias(self):
        topic = find_topic("loom")
        self.assertEqual(topic.key, "virtual-threads")

    def test_every_link_is_official(self):
        allowed = (
            "https://docs.oracle.com/",
            "https://openjdk.org/",
        )
        for topic in TOPICS:
            for link in topic.links:
                self.assertTrue(link.startswith(allowed), link)

    def test_render_text_includes_footer_ready_links(self):
        text = render_text(find_topic("records"))
        self.assertIn("Official docs:", text)
        self.assertIn("https://openjdk.org/jeps/395", text)


if __name__ == "__main__":
    unittest.main()
