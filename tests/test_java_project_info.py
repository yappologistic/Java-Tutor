import tempfile
import textwrap
import unittest
from pathlib import Path

from java_project_info_script import infer_project_info, normalize_version


class JavaProjectInfoTests(unittest.TestCase):
    def test_normalizes_legacy_version(self):
        self.assertEqual(normalize_version("1.8"), "8")

    def test_detects_maven_compiler_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text(
                textwrap.dedent(
                    """\
                    <project xmlns="http://maven.apache.org/POM/4.0.0">
                      <properties>
                        <maven.compiler.release>21</maven.compiler.release>
                      </properties>
                    </project>
                    """
                ),
                encoding="utf-8",
            )
            info = infer_project_info(root)
            self.assertEqual(info["recommended_version"], "21")

    def test_resolves_maven_property_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text(
                textwrap.dedent(
                    """\
                    <project xmlns="http://maven.apache.org/POM/4.0.0">
                      <properties>
                        <java.version>17</java.version>
                      </properties>
                      <build>
                        <plugins>
                          <plugin>
                            <artifactId>maven-compiler-plugin</artifactId>
                            <configuration>
                              <release>${java.version}</release>
                            </configuration>
                          </plugin>
                        </plugins>
                      </build>
                    </project>
                    """
                ),
                encoding="utf-8",
            )
            info = infer_project_info(root)
            self.assertEqual(info["recommended_version"], "17")

    def test_detects_gradle_toolchain(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle.kts").write_text(
                "java { toolchain { languageVersion = JavaLanguageVersion.of(25) } }",
                encoding="utf-8",
            )
            info = infer_project_info(root)
            self.assertIn("25", info["detected_versions"])

    def test_detects_java_version_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".java-version").write_text("17\n", encoding="utf-8")
            info = infer_project_info(root)
            self.assertEqual(info["recommended_version"], "17")

    def test_detects_java_version_from_docker_tag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Dockerfile").write_text("FROM maven:3.9-eclipse-temurin-21\n", encoding="utf-8")
            info = infer_project_info(root)
            self.assertEqual(info["recommended_version"], "21")


if __name__ == "__main__":
    unittest.main()
