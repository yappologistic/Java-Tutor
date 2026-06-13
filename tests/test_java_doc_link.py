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

    def test_api_member_link(self):
        self.assertEqual(
            build_link("api", "java.lang.String#toUpperCase()", "25"),
            "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/String.html#toUpperCase()",
        )

    def test_infers_non_base_module(self):
        self.assertEqual(
            build_link("api", "java.sql.Date", "25"),
            "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Date.html",
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
