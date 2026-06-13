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

    def test_maven_test_file_uses_package_qualified_class_when_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text("<project />", encoding="utf-8")
            test_file = root / "src" / "test" / "java" / "com" / "acme" / "ExampleTest.java"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("package com.acme;\nclass ExampleTest {}", encoding="utf-8")
            result = suggest_commands(root, "src/test/java/com/acme/ExampleTest.java")
            self.assertIn("-Dtest=com.acme.ExampleTest", result["commands"][0]["command"])

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
            self.assertEqual(result["commands"][0]["argv"][0], "javac")

    def test_source_tree_without_build_file_suggests_javac(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "src" / "main" / "java" / "Hello.java"
            source.parent.mkdir(parents=True)
            source.write_text("class Hello {}", encoding="utf-8")
            result = suggest_commands(root)
            self.assertEqual(result["commands"][0]["scope"], "single-file")
            self.assertEqual(result["commands"][0]["argv"], ["javac", str(source)])

    def test_changed_file_with_spaces_is_quoted_in_command_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "space dir"
            root.mkdir()
            changed = root / "Hello World.java"
            changed.write_text("class HelloWorld {}", encoding="utf-8")
            result = suggest_commands(root, "Hello World.java")
            command = result["commands"][0]["command"]
            self.assertIn("javac", command)
            self.assertNotEqual(command, " ".join(result["commands"][0]["argv"]))

    def test_changed_file_outside_root_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "project"
            root.mkdir()
            outside = parent / "OtherTest.java"
            outside.write_text("class OtherTest {}", encoding="utf-8")
            (root / "pom.xml").write_text("<project />", encoding="utf-8")
            result = suggest_commands(root, "../OtherTest.java")
            self.assertIsNone(result["changed_file"])
            self.assertFalse(any(item["scope"] == "narrow" for item in result["commands"]))

    def test_render_text_lists_commands(self):
        result = {"commands": [{"scope": "broad", "command": "mvn test", "reason": "Run tests."}]}
        self.assertIn("`mvn test`", render_text(result))


if __name__ == "__main__":
    unittest.main()
