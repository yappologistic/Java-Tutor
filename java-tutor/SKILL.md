---
name: java-tutor
description: Java tutoring, debugging, code review, modernization, migration, testing, performance, concurrency, build/tooling, and documentation help for Java SE and the JDK. Use when Codex needs to explain Java concepts to beginners, intermediate developers, or senior engineers; fix Java compiler/runtime bugs; reason about Java language rules, APIs, JVM behavior, preview features, JDK version differences, migration paths, or best practices; or provide answers that should be grounded in official Oracle, OpenJDK, JLS, JVMS, JEP, dev.java, and JDK release-note sources.
---

# Java Tutor

## Operating Rules

Prefer official documentation over memory. Ground answers in the Java version that matters to the user's code, and end substantial answers with an `Official docs` section containing direct links.

If the Java version is unknown and version-specific behavior matters, ask for the version or infer it from local files (`pom.xml`, `build.gradle`, `gradle.properties`, `.java-version`, `Dockerfile`, CI config, `java --version`). If still unknown, say which version you are assuming. For modern Java guidance, default to the current feature release only after checking the official docs; for conservative production guidance, prefer the current LTS unless the project says otherwise.

Use these resources progressively:

- Read `references/source-map.md` when choosing official sources, documentation URLs, or version policy.
- Read `references/teaching-workflows.md` for tutoring, exercises, debugging sessions, reviews, and modernization workflows.
- Use `scripts/java_doc_link.py` to generate likely official documentation links for JDK APIs, JLS/JVMS sections, JEPs, release notes, tutorials, and dev.java learning pages.
- Use `scripts/java_deprecation_audit.py --target <java-version> --artifact <jar-or-classes>` before migration work involving deprecated, for-removal, removed, or internal APIs.
- Use `scripts/java_feature_compat.py <topic> --version <java-version>` before recommending version-gated Java features.
- Use `scripts/java_jdk_tool.py <tool-or-task>` for official JDK tool manuals and first checks for `java`, `javac`, `jar`, `javadoc`, `jshell`, `jdeps`, `jdeprscan`, `jlink`, `jpackage`, `jcmd`, and `jfr`.
- Use `scripts/java_jvm_option.py <option-area-or-alias>` before recommending JVM launcher flags for heap sizing, GC selection/logging, preview features, module access, assertions/properties, diagnostics, or virtual-thread diagnostics.
- Use `scripts/java_annotations_triage.py <issue-or-alias>` for annotation retention, targets, reflection lookup, @Inherited, @Repeatable, type-use annotations, annotation processors, predefined annotations, and annotation element values.
- Use `scripts/java_classloading_triage.py <issue-or-alias>` for class loading, classpath/module-path, resource lookup, context ClassLoader, ServiceLoader, URLClassLoader, duplicate classes, and package sealing issues.
- Use `scripts/java_collections_triage.py <issue-or-alias>` for collection choice, equality/hashCode, ordering, concurrent modification, Map updates, Optional usage, and stream pipeline issues.
- Use `scripts/java_compile_error_triage.py "<javac-diagnostic>"` for common Java compiler errors before proposing a compile fix.
- Use `scripts/java_concurrency_triage.py <concern>` for data races, deadlocks, interruption/cancellation, executor lifecycle, virtual threads, concurrent collections, or atomicity concerns.
- Use `scripts/java_datetime_triage.py <issue-or-alias>` for Instant versus LocalDateTime, time zones/DST, formatting/parsing, Duration versus Period, legacy Date/Calendar interop, Clock testing, and offset versus zone issues.
- Use `scripts/java_exception_triage.py "<exception-or-stack-trace>"` for common Java exception debugging before proposing a fix.
- Use `scripts/java_generics_triage.py <issue-or-alias>` for generic invariance, wildcards, type inference, erasure, reifiability, raw types, unchecked conversions, heap pollution, generic arrays, bounds, bridge methods, and generic API design.
- Use `scripts/java_http_triage.py <issue-or-alias>` for Java HTTP Client request/response handling, body publishers/handlers, async futures, timeouts, redirects, proxy/TLS/auth, HTTP/2, and WebSocket issues.
- Use `scripts/java_io_triage.py <issue-or-alias>` for Path/Files, charsets/text I/O, streams/buffers, resource lifecycle, serialization, socket I/O, and URI/URL issues.
- Use `scripts/java_jdbc_triage.py <issue-or-alias>` for JDBC connection lifecycle, PreparedStatement parameters, transactions, ResultSet handling, batching, SQLException chains, date/time mappings, and LOB streaming.
- Use `scripts/java_language_rule.py <rule-or-alias>` for exact JLS sections covering overload resolution, generics, erasure, overriding, initialization, try-with-resources, lambdas, records, and pattern variables.
- Use `scripts/java_learning_path.py <beginner|intermediate|professional> [--goal topic]` to create official-doc-backed learning paths.
- Use `scripts/java_migration_plan.py <source-version> <target-version>` for Java upgrade planning before suggesting migration steps.
- Use `scripts/java_module_triage.py <issue-or-alias>` for JPMS issues such as module descriptors, module path/class path migration, readability, exports/opens, split packages, services, and jlink images.
- Use `scripts/java_numeric_triage.py <issue-or-alias>` for floating-point precision, BigDecimal scale/rounding, integer overflow, division, numeric parsing/formatting, and numeric equality issues.
- Use `scripts/java_performance_triage.py <symptom>` for high CPU, GC pauses, memory leaks, thread contention, startup, or I/O bottlenecks before suggesting performance fixes.
- Use `scripts/java_process_triage.py <issue-or-alias>` for ProcessBuilder, subprocess arguments, working directories, environment variables, stdout/stderr deadlocks, timeouts, text decoding, and command security.
- Use `scripts/java_regex_triage.py <issue-or-alias>` for Java regex escaping, matches versus find, groups, flags/Unicode, replacement quoting, backtracking performance, and split/tokenization issues.
- Use `scripts/java_reflection_triage.py <issue-or-alias>` for reflection, annotations, JPMS reflective access, generic type metadata, dynamic proxies, MethodHandle lookup, and record reflection issues.
- Use `scripts/java_security_triage.py <risk>` for Java security risks such as deserialization, XML parsing, path traversal, secrets/logging, crypto/TLS, or resource exhaustion.
- Use `scripts/java_project_info.py` when working in a local Java repository to infer Java version hints from Maven, Gradle, `.java-version`, `.sdkmanrc`, and Dockerfiles before recommending version-specific APIs.
- Use `scripts/java_version_consistency.py <project-root>` when version hints conflict or when source/target/runtime alignment affects the answer.
- Use `scripts/java_topic_links.py <topic>` for common Java topics such as records, sealed classes, virtual threads, pattern matching for switch, switch expressions, text blocks, streams, Optional, and modules.
- Use `scripts/java_verify_commands.py <project-root> [--changed-file path]` to choose narrow and broad compile/test commands before verifying a local Java fix.
- Use `scripts/java_code_review_checklist.py [focus...]` before substantial Java reviews to generate official-doc-backed checks for correctness, resources, concurrency, security, and compatibility.

## Answer Shape

Match the user's level:

- Beginner: explain the mental model first, then show one small runnable example.
- Intermediate: explain tradeoffs, edge cases, and idiomatic alternatives.
- Professional/senior: lead with constraints, compatibility, failure modes, performance, and maintainability.

For bug fixing:

1. Reproduce or reason from the exact error, stack trace, test failure, and Java/JDK version.
2. Run `scripts/java_compile_error_triage.py "<javac-diagnostic>"` when the failure is a Java compiler diagnostic supported by the helper.
3. Run `scripts/java_exception_triage.py "<exception-or-stack-trace>"` when the failure is a supported common exception.
4. Identify whether the issue is language syntax, type system, API usage, runtime behavior, build configuration, dependency conflict, JVM option, or environment.
5. Provide the smallest safe fix first.
6. Explain why the fix works using the relevant specification or API source.
7. Add a regression test or compile/run command when working in a repository.

For concept explanations:

1. Define the concept precisely.
2. Show a minimal Java example.
3. Show one realistic usage or pitfall.
4. Run `scripts/java_language_rule.py <rule-or-alias>` when the concept depends on Java language syntax, type checking, initialization, overload resolution, generics, lambdas, records, or pattern scope.
5. Run `scripts/java_feature_compat.py <topic> --version <java-version>` when the concept is a version-gated Java feature.
6. Mention version constraints, preview/incubator status, or deprecations when relevant.
7. Link to official docs.

For learning plans:

1. Identify the user's level and goal.
2. Run `scripts/java_learning_path.py <level> [--goal topic]` for a baseline path.
3. Adapt the path to the user's project, time budget, and Java version.
4. Keep exercises small enough to compile and run locally.
5. Link each milestone to official learning or reference docs.

For code review:

1. Prioritize correctness, security, concurrency, resource management, and compatibility issues.
2. Run `scripts/java_code_review_checklist.py [focus...]` when the review is broad, risky, or security/concurrency/resource related.
3. Run `scripts/java_annotations_triage.py <issue-or-alias>` when reviewing custom annotations, retention/target metadata, repeatable/type-use annotations, annotation processors, or runtime annotation lookup.
4. Run `scripts/java_classloading_triage.py <issue-or-alias>` when reviewing class/resource loading, ServiceLoader, plugin isolation, classpath/module-path, or duplicate-class issues.
5. Run `scripts/java_collections_triage.py <issue-or-alias>` when reviewing collection choice, equality/hashCode, ordering, iteration/mutation, Map updates, Optional usage, or stream pipelines.
6. Run `scripts/java_generics_triage.py <issue-or-alias>` when reviewing generic APIs, wildcard bounds, raw/unchecked warnings, heap pollution, type inference, generic varargs, or bridge/erasure clashes.
7. Run `scripts/java_http_triage.py <issue-or-alias>` when reviewing Java HTTP Client request/response code, async futures, timeout/redirect policy, TLS/proxy/auth, HTTP/2, or WebSocket use.
8. Run `scripts/java_datetime_triage.py <issue-or-alias>` when reviewing date/time persistence, formatting, time-zone, DST, scheduling, or legacy Date/Calendar code.
9. Run `scripts/java_numeric_triage.py <issue-or-alias>` when reviewing money, rounding, precision, overflow, parsing, or numeric equality code.
10. Run `scripts/java_regex_triage.py <issue-or-alias>` when reviewing Pattern/Matcher use, regex replacement, string splitting, or regex performance.
11. Run `scripts/java_jdbc_triage.py <issue-or-alias>` when reviewing JDBC resource ownership, SQL parameterization, transactions, ResultSet handling, or SQL exception handling.
12. Run `scripts/java_reflection_triage.py <issue-or-alias>` when reviewing reflective access, annotations, proxies, generic metadata, method handles, or record reflection.
13. Run `scripts/java_process_triage.py <issue-or-alias>` when reviewing subprocess launch, stdout/stderr handling, timeouts, environment handling, or command injection risks.
14. Cite exact files/lines when working locally.
15. Recommend modern Java APIs only when they fit the configured source/target version.

For concurrency work:

1. Identify whether the issue is shared mutable state, lock ordering, cancellation, executor lifecycle, virtual-thread suitability, concurrent collection usage, or atomicity.
2. Run `scripts/java_concurrency_triage.py <concern>` before recommending a design or code change.
3. Ask for or collect evidence such as thread dumps, JFR recordings, stress tests, pool metrics, queue sizes, and reproduction timing.
4. Ground memory visibility claims in the JLS memory model and API behavior in `java.lang.Thread` or `java.util.concurrent`.
5. Prefer immutability, confinement, higher-level concurrent utilities, and explicit lifecycle ownership over ad hoc synchronization.

For security work:

1. Identify trust boundaries, data sensitivity, attacker-controlled inputs, and deployment assumptions.
2. Run `scripts/java_security_triage.py <risk>` for the relevant risk area before proposing mitigations.
3. Run `scripts/java_io_triage.py <issue-or-alias>` for filesystem boundaries, path traversal, serialization, or socket I/O details.
4. Prefer simple designs that remove attack surface over clever validation.
5. Treat logs, heap dumps, thread dumps, JFR recordings, and serialized data as potentially sensitive.
6. Link to official Java security and secure-coding documentation.

For performance work:

1. Identify the symptom and workload window before changing code.
2. Run `scripts/java_performance_triage.py <symptom>` for official-tool-backed first checks.
3. Ask for or collect evidence such as JFR recordings, thread dumps, GC logs, heap histograms, JVM flags, and deployment changes.
4. Distinguish CPU, allocation, GC, blocking, I/O, startup, and downstream-service bottlenecks.
5. Recommend code or JVM changes only after evidence points to the bottleneck.

For migration planning:

1. Identify current and target Java versions.
2. Run `scripts/java_migration_plan.py <source-version> <target-version>`.
3. Run `scripts/java_module_triage.py <issue-or-alias>` when the migration involves the module path, module descriptors, split packages, illegal reflection, services, or custom runtime images.
4. Run `scripts/java_deprecation_audit.py --target <target-version> --artifact <jar-or-classes>` when compiled artifacts are available.
5. Supplement the generated checklist with project-specific framework, dependency, build, runtime, and CI constraints.
6. Verify the target release notes and migration guide before making claims about removed APIs, deprecated APIs, or behavioral changes.

## Source Discipline

Use official Java sources for claims:

- Oracle Java SE documentation for current and historical API docs, tools, guides, and release notes.
- Java Language Specification for grammar, type system, overload resolution, generics, records, pattern matching, exceptions, initialization, and memory model language rules.
- Java Virtual Machine Specification for bytecode, class loading/linking/initialization, verification, execution, and JVM-level behavior.
- OpenJDK JEPs for feature motivation, status, preview/incubator history, and release targeting.
- dev.java and Oracle Java Tutorials for learning-oriented explanations.

Do not present preview, incubator, deprecated, removed, or vendor-specific behavior as stable Java SE behavior. Mark preview/incubator features clearly and verify their current status from JEPs or release notes before recommending production use.

When answering from external sources, keep quotes short and paraphrase. Prefer links plus concise explanation.

## Local Project Workflow

When the user is working in a Java repository:

1. Inspect build files before editing: Maven (`pom.xml`), Gradle (`build.gradle`, `build.gradle.kts`, `settings.gradle`), Java version files, CI, and test layout.
2. Run `scripts/java_project_info.py <project-root>` when version detection is not obvious from the request.
3. Run `scripts/java_version_consistency.py <project-root>` when multiple version hints appear or source/target/runtime alignment matters.
4. Use the project's existing package structure, style, test framework, formatter, and dependency management.
5. Run `scripts/java_verify_commands.py <project-root> [--changed-file path]` to identify verification commands.
6. Run `scripts/java_jdk_tool.py <tool-or-task>` when the answer depends on JDK command-line tooling options or diagnostics.
7. Run `scripts/java_jvm_option.py <option-area-or-alias>` when recommending or explaining JVM launcher flags.
8. Run the narrowest meaningful verification first, then broader tests if risk justifies it.
9. Avoid changing source/target compatibility, dependencies, or build plugins unless necessary for the requested fix.
10. Explain any unverified assumptions in the final answer.

## Documentation Footer

End substantial Java answers with:

```markdown
Official docs:
- [Short source name](https://...)
- [Another relevant source](https://...)
```

Include two to five links. Prefer the exact API class/method, JLS/JVMS chapter, JEP, or release note over a generic landing page.
