import unittest

from java_topic_links_script import TOPICS, find_topic, links_for, payload_for, render_text


class JavaTopicLinksTests(unittest.TestCase):
    def test_finds_topic_by_key(self):
        topic = find_topic("virtual-threads")
        self.assertEqual(topic.minimum_version, "21")
        self.assertIn("https://openjdk.org/jeps/444", links_for(topic, "25"))

    def test_finds_topic_by_alias(self):
        topic = find_topic("loom")
        self.assertEqual(topic.key, "virtual-threads")

    def test_finds_sequenced_collections_by_alias(self):
        topic = find_topic("sequenced map")
        self.assertEqual(topic.key, "sequenced-collections")
        self.assertEqual(topic.minimum_version, "21")
        self.assertIn("https://openjdk.org/jeps/431", links_for(topic, "25"))

    def test_links_for_honors_requested_version(self):
        links = links_for(find_topic("records"), "21")
        self.assertIn("https://openjdk.org/jeps/395", links)
        self.assertTrue(any("/java/javase/21/" in link for link in links), links)
        self.assertFalse(any("/java/javase/25/" in link for link in links), links)

    def test_payload_uses_resolved_links(self):
        payload = payload_for(find_topic("records"), "17")
        self.assertEqual(payload["version"], "17")
        self.assertTrue(any("/java/javase/17/" in link for link in payload["links"]))

    def test_every_link_is_official(self):
        allowed = (
            "https://docs.oracle.com/",
            "https://openjdk.org/",
        )
        for topic in TOPICS:
            for link in links_for(topic, "25"):
                self.assertTrue(link.startswith(allowed), link)

    def test_render_text_includes_footer_ready_links(self):
        text = render_text(find_topic("records"), "25")
        self.assertIn("Official docs:", text)
        self.assertIn("https://openjdk.org/jeps/395", text)


if __name__ == "__main__":
    unittest.main()
