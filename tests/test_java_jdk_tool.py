import unittest

from java_jdk_tool_script import find_tool, official_urls, render_text, tools


class JavaJdkToolTests(unittest.TestCase):
    def test_finds_compiler_alias(self):
        tool = find_tool("compiler")
        self.assertEqual(tool.key, "javac")
        self.assertIn("--release", tool.common_options)

    def test_finds_thread_dump_alias(self):
        tool = find_tool("thread dump")
        self.assertEqual(tool.key, "jcmd")
        self.assertTrue(any("sensitive" in check for check in tool.first_checks))

    def test_unknown_tool_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available tools"):
            find_tool("mvn")

    def test_render_text_contains_options_and_docs(self):
        text = render_text(find_tool("jpackage"))
        self.assertIn("Common options:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("--runtime-image", text)

    def test_official_urls_are_official_sources(self):
        urls = official_urls(tools())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/"), url)

    def test_jfr_troubleshooting_link_honors_requested_version(self):
        tool = find_tool("jfr", version="21")
        self.assertTrue(any("/java/javase/21/troubleshoot/" in url for url in tool.docs), tool.docs)
        self.assertFalse(any("/java/javase/25/troubleshoot/" in url for url in tool.docs), tool.docs)


if __name__ == "__main__":
    unittest.main()
