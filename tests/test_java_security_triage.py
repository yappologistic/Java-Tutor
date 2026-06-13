import unittest

from java_security_triage_script import find_risk, official_urls, render_text, risks


class JavaSecurityTriageTests(unittest.TestCase):
    def test_finds_xml_alias(self):
        risk = find_risk("xxe")
        self.assertEqual(risk.key, "xml-parsing")
        self.assertTrue(any("FEATURE_SECURE_PROCESSING" in check for check in risk.first_checks))

    def test_finds_crypto_alias(self):
        risk = find_risk("tls")
        self.assertEqual(risk.key, "crypto-random")
        self.assertTrue(any("SecureRandom" in item for item in risk.first_checks))

    def test_unknown_risk_has_available_options(self):
        with self.assertRaisesRegex(ValueError, "available risks"):
            find_risk("css")

    def test_render_text_contains_safer_defaults_and_docs(self):
        text = render_text(find_risk("deserialization"))
        self.assertIn("Safer defaults:", text)
        self.assertIn("Official docs:", text)
        self.assertIn("serialization", text.lower())

    def test_official_urls_are_official_sources(self):
        urls = official_urls(risks())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith("https://docs.oracle.com/") or url.startswith("https://www.oracle.com/java/"))


if __name__ == "__main__":
    unittest.main()
