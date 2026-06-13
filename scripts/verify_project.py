#!/usr/bin/env python3
"""Verify the Java Tutor skill project without local Codex-only tooling."""

from __future__ import annotations

import argparse
import html
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "java-tutor"
REQUIRED_FILES = [
    SKILL_DIR / "SKILL.md",
    SKILL_DIR / "agents" / "openai.yaml",
    SKILL_DIR / "references" / "source-map.md",
    SKILL_DIR / "references" / "teaching-workflows.md",
    SKILL_DIR / "scripts" / "java_doc_link.py",
    SKILL_DIR / "scripts" / "java_code_review_checklist.py",
    SKILL_DIR / "scripts" / "java_annotations_triage.py",
    SKILL_DIR / "scripts" / "java_classloading_triage.py",
    SKILL_DIR / "scripts" / "java_collections_triage.py",
    SKILL_DIR / "scripts" / "java_compile_error_triage.py",
    SKILL_DIR / "scripts" / "java_concurrency_triage.py",
    SKILL_DIR / "scripts" / "java_datetime_triage.py",
    SKILL_DIR / "scripts" / "java_deprecation_audit.py",
    SKILL_DIR / "scripts" / "java_exception_triage.py",
    SKILL_DIR / "scripts" / "java_feature_compat.py",
    SKILL_DIR / "scripts" / "java_generics_triage.py",
    SKILL_DIR / "scripts" / "java_http_triage.py",
    SKILL_DIR / "scripts" / "java_io_triage.py",
    SKILL_DIR / "scripts" / "java_jdbc_triage.py",
    SKILL_DIR / "scripts" / "java_jdk_tool.py",
    SKILL_DIR / "scripts" / "java_jvm_option.py",
    SKILL_DIR / "scripts" / "java_language_rule.py",
    SKILL_DIR / "scripts" / "java_learning_path.py",
    SKILL_DIR / "scripts" / "java_migration_plan.py",
    SKILL_DIR / "scripts" / "java_module_triage.py",
    SKILL_DIR / "scripts" / "java_numeric_triage.py",
    SKILL_DIR / "scripts" / "java_performance_triage.py",
    SKILL_DIR / "scripts" / "java_process_triage.py",
    SKILL_DIR / "scripts" / "java_project_info.py",
    SKILL_DIR / "scripts" / "java_regex_triage.py",
    SKILL_DIR / "scripts" / "java_reflection_triage.py",
    SKILL_DIR / "scripts" / "java_security_triage.py",
    SKILL_DIR / "scripts" / "java_text_triage.py",
    SKILL_DIR / "scripts" / "java_topic_links.py",
    SKILL_DIR / "scripts" / "java_verify_commands.py",
    SKILL_DIR / "scripts" / "java_version_consistency.py",
    ROOT / "README.md",
    ROOT / "INSTALL.md",
    ROOT / "LICENSE",
    ROOT / "install.ps1",
    ROOT / "install.sh",
    ROOT / ".gitattributes",
    ROOT / ".gitignore",
]
OFFICIAL_URLS = [
    "https://docs.oracle.com/en/java/javase/",
    "https://www.oracle.com/java/technologies/downloads/",
    "https://docs.oracle.com/en/java/javase/26/",
    "https://docs.oracle.com/en/java/javase/25/docs/api/",
    "https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html",
    "https://docs.oracle.com/en/java/javase/25/docs/specs/man/jar.html",
    "https://docs.oracle.com/en/java/javase/25/docs/specs/man/javadoc.html",
    "https://docs.oracle.com/en/java/javase/25/docs/specs/man/jfr.html",
    "https://docs.oracle.com/en/java/javase/25/docs/specs/man/jlink.html",
    "https://docs.oracle.com/en/java/javase/25/docs/specs/man/jpackage.html",
    "https://docs.oracle.com/en/java/javase/25/docs/specs/man/jshell.html",
    "https://docs.oracle.com/en/java/javase/25/docs/specs/man/jdeprscan.html",
    "https://docs.oracle.com/en/java/javase/25/docs/specs/man/jdeps.html",
    "https://docs.oracle.com/en/java/javase/25/security/index.html",
    "https://docs.oracle.com/en/java/javase/25/security/java-security-overview1.html",
    "https://docs.oracle.com/en/java/javase/25/migrate/index.html",
    "https://docs.oracle.com/javase/specs/jls/se25/html/index.html",
    "https://docs.oracle.com/javase/specs/jvms/se25/html/index.html",
    "https://www.oracle.com/java/technologies/javase/26all-relnotes.html",
    "https://www.oracle.com/java/technologies/javase/25all-relnotes.html",
    "https://www.oracle.com/java/technologies/javase/seccodeguide.html",
    "https://openjdk.org/jeps/0",
    "https://dev.java/learn/",
    "https://docs.oracle.com/javase/tutorial/",
    "https://dev.java/learn/getting-started/",
    "https://dev.java/learn/language-basics/",
    "https://dev.java/learn/classes-objects/",
    "https://dev.java/learn/api/collections-framework/",
    "https://dev.java/learn/api/streams/",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Comparable.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Collection.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Collections.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Comparator.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Iterator.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Set.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Collectors.html",
    "https://dev.java/learn/jvm/jfr/",
    "https://docs.oracle.com/en/java/javase/25/troubleshoot/diagnostic-tools.html",
    "https://docs.oracle.com/en/java/javase/25/troubleshoot/troubleshoot-performance-issues-using-jfr.html",
    "https://docs.oracle.com/en/java/javase/25/migrate/removed-apis.html",
    "https://docs.oracle.com/en/java/javase/25/migrate/removed-tools-and-components.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/deprecated-list.html",
    "https://docs.oracle.com/en/java/javase/25/core/serialization-filtering1.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.xml/javax/xml/XMLConstants.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/security/SecureRandom.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/nio/file/Path.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/nio/file/Files.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/nio/charset/Charset.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/nio/charset/StandardCharsets.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/InputStream.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/OutputStream.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/Reader.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/Writer.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/ObjectInputStream.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/Socket.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/ServerSocket.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/URI.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/URL.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/Authenticator.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/ProxySelector.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/package-summary.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Connection.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/javax/sql/DataSource.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/DriverManager.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Statement.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/PreparedStatement.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/CallableStatement.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/ResultSet.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/ResultSetMetaData.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/SQLException.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/SQLWarning.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/BatchUpdateException.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/SQLTimeoutException.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/SQLIntegrityConstraintViolationException.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Savepoint.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Blob.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Clob.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Date.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Time.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Timestamp.html",
    "https://docs.oracle.com/javase/tutorial/essential/io/path.html",
    "https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Thread.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/InterruptedException.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/package-summary.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ExecutorService.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Future.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/atomic/package-summary.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/locks/package-summary.html",
    "https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/package-summary.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/Instant.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/LocalDateTime.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/ZonedDateTime.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/ZoneId.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/zone/ZoneRules.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/format/DateTimeFormatter.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/format/DateTimeParseException.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/Duration.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/Period.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/temporal/ChronoUnit.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Date.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Calendar.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/TimeZone.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/text/SimpleDateFormat.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/Clock.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/OffsetDateTime.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/ZoneOffset.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/math/BigDecimal.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/math/BigInteger.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/math/RoundingMode.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Double.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Float.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Integer.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Long.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Math.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/StrictMath.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ArithmeticException.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/NumberFormatException.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/text/NumberFormat.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/text/DecimalFormat.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Locale.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/regex/Pattern.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/regex/Matcher.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/regex/PatternSyntaxException.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Class.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Member.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Method.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Constructor.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Field.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/AccessibleObject.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/InvocationTargetException.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Modifier.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/ParameterizedType.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/AnnotatedElement.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Proxy.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/InvocationHandler.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/RecordComponent.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/annotation/Annotation.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/annotation/Retention.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/annotation/RetentionPolicy.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/annotation/Target.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/invoke/MethodHandles.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/invoke/MethodHandle.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/invoke/MethodHandles.Lookup.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ProcessBuilder.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Process.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ProcessHandle.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Runtime.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/File.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/TimeUnit.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/SecurityManager.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/javax/net/ssl/SSLContext.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/javax/net/ssl/SSLParameters.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpRequest.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpRequest.BodyPublishers.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpResponse.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpResponse.BodyHandlers.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpResponse.BodySubscribers.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/WebSocket.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpTimeoutException.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ClassLoader.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ModuleLayer.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/module/ModuleFinder.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/URLClassLoader.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/jar/JarFile.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/SecurityException.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Module.html",
    "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/ServiceLoader.html",
    "https://docs.oracle.com/javase/specs/jls/se25/html/jls-7.html#jls-7.7",
    "https://docs.oracle.com/javase/specs/jls/se25/html/jls-7.html#jls-7.7.1",
    "https://docs.oracle.com/javase/specs/jls/se25/html/jls-7.html#jls-7.7.2",
    "https://docs.oracle.com/javase/specs/jls/se25/html/jls-7.html#jls-7.7.3",
    "https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.10.3",
    "https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.21.1",
    "https://docs.oracle.com/javase/specs/jls/se25/html/jls-9.html",
    "https://openjdk.org/jeps/12",
]
RELEASE_FACT_CHECKS = [
    {
        "name": "Oracle downloads latest release",
        "url": "https://www.oracle.com/java/technologies/downloads/",
        "required": ["JDK 26 is the latest release of the Java SE Platform"],
    },
    {
        "name": "Oracle downloads latest LTS",
        "url": "https://www.oracle.com/java/technologies/downloads/",
        "required": ["JDK 25 is the latest Long-Term Support (LTS) release of the Java SE Platform"],
    },
    {
        "name": "Oracle Java SE docs current versions",
        "url": "https://docs.oracle.com/en/java/javase/",
        "required": ["Current Java SE Versions", "JDK 26", "JDK 25", "JDK 21", "JDK 17", "JDK 11", "JDK 8"],
    },
    {
        "name": "OpenJDK JDK 25 General Availability",
        "url": "https://openjdk.org/projects/jdk/25/",
        "required": ["JDK 25 reached General Availability on 16 September 2025"],
    },
    {
        "name": "Oracle JDK 26 release notes",
        "url": "https://www.oracle.com/java/technologies/javase/26all-relnotes.html",
        "required": ["JDK 26.0.1", "April 21, 2026", "JDK 26", "March 17, 2026"],
    },
]


def topic_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_topic_links
    finally:
        sys.path.pop(0)
    for topic in java_topic_links.TOPICS:
        yield from java_topic_links.links_for(topic, "25")


def exception_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_exception_triage
    finally:
        sys.path.pop(0)
    for item in java_exception_triage.EXCEPTIONS:
        yield java_exception_triage.api_link(item.api_class, "25")


def http_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_http_triage
    finally:
        sys.path.pop(0)
    yield from java_http_triage.official_urls(java_http_triage.issues())


def review_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_code_review_checklist
    finally:
        sys.path.pop(0)
    yield from java_code_review_checklist.official_urls(java_code_review_checklist.select_areas())


def compile_error_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_compile_error_triage
    finally:
        sys.path.pop(0)
    yield from java_compile_error_triage.official_urls(java_compile_error_triage.diagnostics())


def annotations_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_annotations_triage
    finally:
        sys.path.pop(0)
    yield from java_annotations_triage.official_urls(java_annotations_triage.issues())


def classloading_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_classloading_triage
    finally:
        sys.path.pop(0)
    yield from java_classloading_triage.official_urls(java_classloading_triage.issues())


def collections_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_collections_triage
    finally:
        sys.path.pop(0)
    yield from java_collections_triage.official_urls(java_collections_triage.issues())


def concurrency_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_concurrency_triage
    finally:
        sys.path.pop(0)
    yield from java_concurrency_triage.official_urls(java_concurrency_triage.concerns())


def datetime_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_datetime_triage
    finally:
        sys.path.pop(0)
    yield from java_datetime_triage.official_urls(java_datetime_triage.issues())


def generics_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_generics_triage
    finally:
        sys.path.pop(0)
    yield from java_generics_triage.official_urls(java_generics_triage.issues())


def language_rule_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_language_rule
    finally:
        sys.path.pop(0)
    yield from java_language_rule.official_urls(java_language_rule.rules())


def io_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_io_triage
    finally:
        sys.path.pop(0)
    yield from java_io_triage.official_urls(java_io_triage.issues())


def jdbc_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_jdbc_triage
    finally:
        sys.path.pop(0)
    yield from java_jdbc_triage.official_urls(java_jdbc_triage.issues())


def jdk_tool_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_jdk_tool
    finally:
        sys.path.pop(0)
    yield from java_jdk_tool.official_urls(java_jdk_tool.tools())


def jvm_option_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_jvm_option
    finally:
        sys.path.pop(0)
    yield from java_jvm_option.official_urls(java_jvm_option.areas())


def module_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_module_triage
    finally:
        sys.path.pop(0)
    yield from java_module_triage.official_urls(java_module_triage.issues())


def numeric_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_numeric_triage
    finally:
        sys.path.pop(0)
    yield from java_numeric_triage.official_urls(java_numeric_triage.issues())


def regex_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_regex_triage
    finally:
        sys.path.pop(0)
    yield from java_regex_triage.official_urls(java_regex_triage.issues())


def reflection_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_reflection_triage
    finally:
        sys.path.pop(0)
    yield from java_reflection_triage.official_urls(java_reflection_triage.issues())


def learning_path_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_learning_path
    finally:
        sys.path.pop(0)
    for path in java_learning_path.paths():
        yield from java_learning_path.official_urls(path)


def version_consistency_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_version_consistency
    finally:
        sys.path.pop(0)
    yield from java_version_consistency.official_urls()


def performance_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_performance_triage
    finally:
        sys.path.pop(0)
    yield from java_performance_triage.official_urls(java_performance_triage.symptoms())


def process_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_process_triage
    finally:
        sys.path.pop(0)
    yield from java_process_triage.official_urls(java_process_triage.issues())


def deprecation_audit_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_deprecation_audit
    finally:
        sys.path.pop(0)
    yield from java_deprecation_audit.official_urls("25")


def security_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_security_triage
    finally:
        sys.path.pop(0)
    yield from java_security_triage.official_urls(java_security_triage.risks())


def text_triage_urls() -> Iterable[str]:
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        import java_text_triage
    finally:
        sys.path.pop(0)
    yield from java_text_triage.official_urls(java_text_triage.issues())


def run(command: list[str], *, timeout: int = 30) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, timeout=timeout, check=True)


def run_with_env(command: list[str], env: dict[str, str], *, timeout: int = 30, cwd: Path = ROOT) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, env=env, timeout=timeout, check=True)


def run_with_env_expect_failure(command: list[str], env: dict[str, str], *, timeout: int = 30, cwd: Path = ROOT) -> None:
    print("+ !", " ".join(command))
    result = subprocess.run(command, cwd=cwd, env=env, timeout=timeout)
    if result.returncode == 0:
        raise AssertionError(f"expected command to fail: {' '.join(command)}")


def run_with_env_input(
    command: list[str],
    env: dict[str, str],
    input_text: str,
    *,
    timeout: int = 30,
    cwd: Path = ROOT,
) -> None:
    print("+", " ".join(command), "< stdin")
    subprocess.run(command, cwd=cwd, env=env, input=input_text.encode("utf-8"), timeout=timeout, check=True)


def bash_visible_path(shell: str, path: Path) -> str:
    result = subprocess.run(
        [shell, "-lc", "pwd"],
        cwd=path if path.is_dir() else path.parent,
        text=True,
        capture_output=True,
        timeout=10,
        check=True,
    )
    bash_cwd = result.stdout.strip()
    return bash_cwd if path.is_dir() else f"{bash_cwd}/{path.name}"


def bash_env_prefix(values: dict[str, str]) -> str:
    return " ".join(f"{key}={shlex.quote(value)}" for key, value in values.items())


def run_bash_command(shell: str, command: str, *, cwd: Path, timeout: int = 30) -> None:
    run_with_env([shell, "-lc", command], os.environ.copy(), timeout=timeout, cwd=cwd)


def run_bash_command_expect_failure(shell: str, command: str, *, cwd: Path, timeout: int = 30) -> None:
    run_with_env_expect_failure([shell, "-lc", command], os.environ.copy(), timeout=timeout, cwd=cwd)


def run_bash_command_input(shell: str, command: str, input_text: str, *, cwd: Path, timeout: int = 30) -> None:
    run_with_env_input([shell, "-lc", command], os.environ.copy(), input_text, timeout=timeout, cwd=cwd)


def normalize_text(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(text.split())


def check_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not path.is_file()]
    if missing:
        raise AssertionError("Missing required files:\n" + "\n".join(str(path) for path in missing))


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        raise AssertionError("SKILL.md must start with YAML frontmatter")

    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            raise AssertionError(f"Invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def check_skill_metadata() -> None:
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    fields = parse_frontmatter(text)
    if fields.get("name") != "java-tutor":
        raise AssertionError("SKILL.md frontmatter name must be java-tutor")
    description = fields.get("description", "")
    if len(description) < 120:
        raise AssertionError("SKILL.md description is too short for reliable triggering")
    for token in ["Java", "debug", "official", "JLS", "JEP"]:
        if token not in description:
            raise AssertionError(f"SKILL.md description should mention {token!r}")
    if "TODO" in text:
        raise AssertionError("SKILL.md still contains TODO text")

    agent_yaml = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if "Use $java-tutor" not in agent_yaml:
        raise AssertionError("agents/openai.yaml default_prompt must mention $java-tutor")


def check_docs() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    install = (ROOT / "INSTALL.md").read_text(encoding="utf-8")
    combined = readme + "\n" + install
    for phrase in [
        "One-line install",
        "One-line update",
        "One-line uninstall",
        "Windows",
        "Linux",
        "macOS",
        "CODEX_GLOBAL_HOME",
        "MIT License",
        "UseBasicParsing",
        "Pinned release pattern",
    ]:
        if phrase not in combined:
            raise AssertionError(f"Documentation should mention {phrase!r}")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if "!gradle/wrapper/gradle-wrapper.jar" not in gitignore:
        raise AssertionError(".gitignore should allow the standard Gradle wrapper jar")


def check_shell_syntax() -> None:
    shell = os.environ.get("SHELLCHECK_SH") or shutil.which("bash") or "sh"
    try:
        run([shell, "-n", "./install.sh"])
    except FileNotFoundError:
        print("Skipping install.sh syntax check: bash/sh is not available")


def check_installers() -> None:
    with tempfile.TemporaryDirectory(prefix="java-tutor-verify-") as temp_dir:
        temp_path = Path(temp_dir)
        archive_zip = create_archive_fixture(temp_path, "zip")
        archive_tgz = create_archive_fixture(temp_path, "gztar")

        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if powershell:
            check_powershell_installer(powershell, temp_path / "ps-local-home", ROOT / "install.ps1")
            remote_dir = temp_path / "ps-archive-script"
            remote_dir.mkdir()
            remote_script = remote_dir / "install.ps1"
            shutil.copy2(ROOT / "install.ps1", remote_script)
            check_powershell_installer(
                powershell,
                temp_path / "ps-archive-home",
                remote_script,
                archive_url=str(archive_zip),
            )
        else:
            print("Skipping install.ps1 smoke test: PowerShell is not available")

        shell = shutil.which("bash")
        if shell:
            check_shell_installer(shell, temp_path / "sh-local-home", ROOT / "install.sh")
            remote_dir = temp_path / "sh-archive-script"
            remote_dir.mkdir()
            remote_script = remote_dir / "install.sh"
            shutil.copy2(ROOT / "install.sh", remote_script)
            check_shell_installer(shell, temp_path / "sh-archive-home", remote_script, archive_url=str(archive_tgz))
            check_shell_stream_installer(shell, temp_path / "sh-stream-home", archive_url=str(archive_tgz))
        else:
            print("Skipping install.sh smoke test: bash is not available")


def create_archive_fixture(temp_path: Path, format_name: str) -> Path:
    archive_parent = temp_path / f"archive-{format_name}"
    fixture_root = archive_parent / "Java-Tutor-main"
    shutil.copytree(SKILL_DIR, fixture_root / "java-tutor")
    shutil.copy2(ROOT / "LICENSE", fixture_root / "LICENSE")
    archive_base = temp_path / f"java-tutor-fixture-{format_name}"
    return Path(shutil.make_archive(str(archive_base), format_name, root_dir=archive_parent, base_dir="Java-Tutor-main"))


def assert_installed_payload(home: Path, installer_name: str) -> None:
    target = home / "skills" / "java-tutor"
    if not (target / "SKILL.md").is_file():
        raise AssertionError(f"{installer_name} did not install SKILL.md")
    if not (target / ".install-info").is_file():
        raise AssertionError(f"{installer_name} did not write install metadata")
    if not (target / "LICENSE").is_file():
        raise AssertionError(f"{installer_name} did not install LICENSE")


def check_powershell_installer(
    powershell: str,
    home: Path,
    script: Path,
    *,
    archive_url: str | None = None,
) -> None:
    env = os.environ.copy()
    env["CODEX_HOME"] = str(home)
    if archive_url:
        env["JAVA_TUTOR_ARCHIVE_URL"] = archive_url
    command_base = [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)]
    run_with_env([*command_base, "-Action", "Status"], env)
    run_with_env(command_base, env)
    assert_installed_payload(home, "install.ps1")
    run_with_env([*command_base, "-Action", "Status"], env)
    run_with_env([*command_base, "-Action", "Update"], env)
    assert_installed_payload(home, "install.ps1 update")
    run_with_env([*command_base, "-Action", "Uninstall"], env)
    if (home / "skills" / "java-tutor" / "SKILL.md").exists():
        raise AssertionError("install.ps1 uninstall left SKILL.md behind")
    assert_powershell_refuses_non_skill_uninstall(powershell, home, command_base, env)


def check_shell_installer(shell: str, home: Path, script: Path, *, archive_url: str | None = None) -> None:
    env_values = {"CODEX_HOME": bash_visible_path(shell, home)}
    if archive_url:
        env_values["JAVA_TUTOR_ARCHIVE_URL"] = (
            bash_visible_path(shell, Path(archive_url)) if Path(archive_url).exists() else archive_url
        )
    prefix = bash_env_prefix(env_values)
    script_arg = f"./{script.name}"
    quoted_script = shlex.quote(script_arg)
    run_bash_command(shell, f"{prefix} bash {quoted_script} status", cwd=script.parent)
    run_bash_command(shell, f"{prefix} bash {quoted_script}", cwd=script.parent)
    assert_installed_payload(home, "install.sh")
    run_bash_command(shell, f"{prefix} bash {quoted_script} status", cwd=script.parent)
    run_bash_command(shell, f"{prefix} bash {quoted_script} update", cwd=script.parent)
    assert_installed_payload(home, "install.sh update")
    run_bash_command(shell, f"{prefix} bash {quoted_script} uninstall", cwd=script.parent)
    if (home / "skills" / "java-tutor" / "SKILL.md").exists():
        raise AssertionError("install.sh uninstall left SKILL.md behind")
    assert_shell_refuses_non_skill_uninstall(shell, home, prefix, quoted_script, script.parent)


def check_shell_stream_installer(shell: str, home: Path, *, archive_url: str) -> None:
    env_values = {
        "CODEX_HOME": bash_visible_path(shell, home),
        "JAVA_TUTOR_ARCHIVE_URL": bash_visible_path(shell, Path(archive_url)) if Path(archive_url).exists() else archive_url,
    }
    prefix = bash_env_prefix(env_values)
    script_text = (ROOT / "install.sh").read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    run_bash_command_input(shell, f"{prefix} bash -s -- status", script_text, cwd=ROOT)
    run_bash_command_input(shell, f"{prefix} bash -s", script_text, cwd=ROOT)
    assert_installed_payload(home, "streamed install.sh")
    run_bash_command_input(shell, f"{prefix} bash -s -- update", script_text, cwd=ROOT)
    assert_installed_payload(home, "streamed install.sh update")
    run_bash_command_input(shell, f"{prefix} bash -s -- uninstall", script_text, cwd=ROOT)
    if (home / "skills" / "java-tutor" / "SKILL.md").exists():
        raise AssertionError("streamed install.sh uninstall left SKILL.md behind")


def assert_powershell_refuses_non_skill_uninstall(
    powershell: str,
    home: Path,
    command_base: list[str],
    env: dict[str, str],
) -> None:
    target = home / "skills" / "java-tutor"
    target.mkdir(parents=True, exist_ok=True)
    marker = target / "not-a-skill.txt"
    marker.write_text("do not delete\n", encoding="utf-8")
    run_with_env_expect_failure([*command_base, "-Action", "Uninstall"], env)
    if not marker.exists():
        raise AssertionError("install.ps1 deleted a non-skill install target")
    shutil.rmtree(target)


def assert_shell_refuses_non_skill_uninstall(
    shell: str,
    home: Path,
    prefix: str,
    quoted_script: str,
    cwd: Path,
) -> None:
    target = home / "skills" / "java-tutor"
    target.mkdir(parents=True, exist_ok=True)
    marker = target / "not-a-skill.txt"
    marker.write_text("do not delete\n", encoding="utf-8")
    run_bash_command_expect_failure(shell, f"{prefix} bash {quoted_script} uninstall", cwd=cwd)
    if not marker.exists():
        raise AssertionError("install.sh deleted a non-skill install target")
    shutil.rmtree(target)


def run_tests() -> None:
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests"])


def check_official_links() -> None:
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "java-tutor-project-verifier/1.0")]
    for url in sorted(
        set(
            [
                *OFFICIAL_URLS,
                *topic_urls(),
                *exception_urls(),
                *review_urls(),
                *annotations_triage_urls(),
                *classloading_triage_urls(),
                *collections_triage_urls(),
                *compile_error_urls(),
                *concurrency_triage_urls(),
                *datetime_triage_urls(),
                *generics_triage_urls(),
                *http_triage_urls(),
                *io_triage_urls(),
                *jdbc_triage_urls(),
                *jdk_tool_urls(),
                *jvm_option_urls(),
                *language_rule_urls(),
                *learning_path_urls(),
                *module_triage_urls(),
                *numeric_triage_urls(),
                *regex_triage_urls(),
                *reflection_triage_urls(),
                *version_consistency_urls(),
                *performance_urls(),
                *process_triage_urls(),
                *deprecation_audit_urls(),
                *security_triage_urls(),
                *text_triage_urls(),
            ]
        )
    ):
        print("+ HEAD", url)
        status = checked_url_status(opener, url)
        if status >= 400:
            raise AssertionError(f"{url} returned HTTP {status}")
        check_url_fragment(opener, url)


def checked_url_status(opener: urllib.request.OpenerDirector, url: str) -> int:
    last_error: BaseException | None = None
    for attempt in range(1, 4):
        try:
            request = urllib.request.Request(url, method="HEAD")
            with opener.open(request, timeout=30) as response:
                return response.status
        except urllib.error.HTTPError as exc:
            if exc.code in {403, 405}:
                request = urllib.request.Request(url, method="GET")
                with opener.open(request, timeout=30) as response:
                    return response.status
            raise
        except (TimeoutError, socket.timeout, urllib.error.URLError) as exc:
            last_error = exc
            if attempt == 3:
                break
            print(f"  retry {attempt}/2 after transient fetch failure: {exc}")
    assert last_error is not None
    raise last_error


def check_url_fragment(opener: urllib.request.OpenerDirector, url: str) -> None:
    base_url, fragment = urllib.parse.urldefrag(url)
    if not fragment:
        return
    request = urllib.request.Request(base_url, method="GET")
    with opener.open(request, timeout=30) as response:
        content_type = response.headers.get_content_charset() or "utf-8"
        page = response.read().decode(content_type, errors="replace")
    escaped = re.escape(fragment)
    if not re.search(rf'\b(?:id|name)=["\']{escaped}["\']', page):
        raise AssertionError(f"{url} fragment was not found as an id/name anchor")


def check_release_facts() -> None:
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "java-tutor-project-verifier/1.0")]
    for check in RELEASE_FACT_CHECKS:
        url = check["url"]
        print("+ FACT", check["name"], url)
        with opener.open(url, timeout=20) as response:
            content_type = response.headers.get_content_charset() or "utf-8"
            page = normalize_text(response.read().decode(content_type, errors="replace"))
        for required in check["required"]:
            if normalize_text(required) not in page:
                raise AssertionError(f"{check['name']} missing expected official text: {required!r}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-links", action="store_true", help="Check reachability of official Java source URLs")
    args = parser.parse_args(argv)

    check_required_files()
    check_skill_metadata()
    check_docs()
    check_shell_syntax()
    check_installers()
    run_tests()
    if args.check_links:
        check_official_links()
        check_release_facts()
    print("Project verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
