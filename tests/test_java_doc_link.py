import unittest

from java_tutor_script import build_link


class JavaDocLinkTests(unittest.TestCase):
    def test_api_class_link(self):
        self.assertEqual(
            build_link("api", "java.util.Optional", "25"),
            "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Optional.html",
        )

    def test_api_package_link(self):
        self.assertEqual(
            build_link("api", "java.util.concurrent.*", "21"),
            "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/package-summary.html",
        )

    def test_java_8_api_package_link_uses_legacy_doc_shape(self):
        self.assertEqual(
            build_link("api", "java.util.stream.*", "8"),
            "https://docs.oracle.com/javase/8/docs/api/java/util/stream/package-summary.html",
        )

    def test_api_member_link(self):
        self.assertEqual(
            build_link("api", "java.lang.String#toUpperCase()", "25"),
            "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/String.html#toUpperCase()",
        )

    def test_nested_class_link(self):
        self.assertEqual(
            build_link("api", "java.util.Map.Entry", "25"),
            "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Map.Entry.html",
        )

    def test_java_8_api_class_link_uses_legacy_doc_shape(self):
        self.assertEqual(
            build_link("api", "java.util.Optional", "8"),
            "https://docs.oracle.com/javase/8/docs/api/java/util/Optional.html",
        )

    def test_infers_non_base_module(self):
        self.assertEqual(
            build_link("api", "java.sql.Date", "25"),
            "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Date.html",
        )

    def test_longest_prefix_module_inference(self):
        self.assertEqual(
            build_link("api", "java.awt.datatransfer.Clipboard", "25"),
            "https://docs.oracle.com/en/java/javase/25/docs/api/java.datatransfer/java/awt/datatransfer/Clipboard.html",
        )

    def test_java_compiler_module_inference(self):
        self.assertEqual(
            build_link("api", "javax.annotation.processing.Processor", "25"),
            "https://docs.oracle.com/en/java/javase/25/docs/api/java.compiler/javax/annotation/processing/Processor.html",
        )

    def test_security_jgss_module_inference(self):
        self.assertEqual(
            build_link("api", "javax.security.auth.kerberos.KerberosPrincipal", "25"),
            "https://docs.oracle.com/en/java/javase/25/docs/api/java.security.jgss/javax/security/auth/kerberos/KerberosPrincipal.html",
        )

    def test_jls_link(self):
        self.assertEqual(
            build_link("jls", "15.12", "25"),
            "https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.12",
        )

    def test_jep_link(self):
        self.assertEqual(build_link("jep", "444", "25"), "https://openjdk.org/jeps/444")


if __name__ == "__main__":
    unittest.main()
