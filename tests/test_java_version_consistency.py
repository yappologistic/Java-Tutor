import tempfile
import textwrap
import unittest
from pathlib import Path

from java_version_consistency_script import analyze, official_urls, parse_major, render_text


class JavaVersionConsistencyTests(unittest.TestCase):
    def test_parse_major_uses_project_normalization(self):
        self.assertEqual(parse_major("1.8"), 8)
        self.assertEqual(parse_major("17.0.10-tem"), 17)

    def test_reports_no_hints(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = analyze(Path(tmp))
            self.assertEqual(result["detected_versions"], [])
            self.assertEqual(result["issues"][0]["code"], "no-version-hints")

    def test_reports_mixed_build_and_runtime_hints(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text(
                textwrap.dedent(
                    """\
                    <project xmlns="http://maven.apache.org/POM/4.0.0">
                      <properties>
                        <maven.compiler.release>11</maven.compiler.release>
                      </properties>
                    </project>
                    """
                ),
                encoding="utf-8",
            )
            (root / ".java-version").write_text("21\n", encoding="utf-8")
            result = analyze(root)
            codes = [issue["code"] for issue in result["issues"]]
            self.assertIn("mixed-version-hints", codes)
            self.assertIn("runtime-newer-than-compile-baseline", codes)

    def test_legacy_baseline_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".java-version").write_text("8\n", encoding="utf-8")
            result = analyze(root)
            self.assertIn("legacy-baseline", [issue["code"] for issue in result["issues"]])

    def test_render_text_has_docs_footer(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = render_text(analyze(Path(tmp)))
            self.assertIn("Java version consistency", text)
            self.assertIn("Official docs:", text)

    def test_official_urls_are_oracle_docs(self):
        for url in official_urls():
            self.assertTrue(url.startswith("https://docs.oracle.com/"))


if __name__ == "__main__":
    unittest.main()
