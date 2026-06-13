import tempfile
import unittest
from pathlib import Path

from java_verify_commands_script import render_text, suggest_commands


class JavaVerifyCommandsTests(unittest.TestCase):
    def test_maven_project_suggests_test_compile_and_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text("<project />", encoding="utf-8")
            result = suggest_commands(root)
            commands = [item["command"] for item in result["commands"]]
            self.assertIn("mvn test-compile", commands)
            self.assertIn("mvn test", commands)

    def test_maven_test_file_suggests_narrow_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text("<project />", encoding="utf-8")
            test_file = root / "src" / "test" / "java" / "ExampleTest.java"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("class ExampleTest {}", encoding="utf-8")
            result = suggest_commands(root, "src/test/java/ExampleTest.java")
            self.assertEqual(result["commands"][0]["scope"], "narrow")
            self.assertIn("-Dtest=ExampleTest", result["commands"][0]["command"])

    def test_gradle_project_prefers_wrapper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle").write_text("plugins { id 'java' }", encoding="utf-8")
            (root / "gradlew").write_text("#!/usr/bin/env sh\n", encoding="utf-8")
            result = suggest_commands(root)
            commands = [item["command"] for item in result["commands"]]
            self.assertIn("./gradlew compileJava compileTestJava", commands)
            self.assertIn("./gradlew test", commands)

    def test_single_file_project_suggests_javac(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Hello.java").write_text("class Hello {}", encoding="utf-8")
            result = suggest_commands(root)
            self.assertEqual(result["commands"][0]["scope"], "single-file")
            self.assertIn("javac", result["commands"][0]["command"])

    def test_render_text_lists_commands(self):
        result = {"commands": [{"scope": "broad", "command": "mvn test", "reason": "Run tests."}]}
        self.assertIn("`mvn test`", render_text(result))


if __name__ == "__main__":
    unittest.main()
