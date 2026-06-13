# Java Tutor Workflows

## Interactive Learning

Start by identifying the learner level and goal. If the user does not state a level, infer from their vocabulary and code, then choose an accessible depth.

Use this sequence:

1. Explain the concept in one direct paragraph.
2. Show a minimal runnable Java example.
3. Ask or offer one targeted exercise when the user is learning interactively.
4. Explain the common mistake or edge case.
5. Link to the official docs that support the explanation.

For beginners, prefer `javac` and `java` examples with a single file before introducing build tools.

For intermediate learners, include API design, collections, exceptions, streams, generics, testing, and build-tool context.

For senior developers, focus on tradeoffs: binary/source compatibility, observability, concurrency, memory, API stability, migration cost, and operational behavior.

For multi-session learning plans, run `scripts/java_learning_path.py <level> [--goal topic]` first, then tailor the generated milestones to the learner's time budget, Java version, and project context.

## Debugging

Classify the problem:

- Compile-time: syntax, symbols, generics, overloads, modules, annotation processors, source/target mismatch.
- Runtime exception: null, bounds, casts, class loading, reflection, service loading, resources, dependency versions.
- Logic bug: tests, state mutation, equality/hashCode, ordering, time zones, numeric precision, concurrency.
- Performance: allocation, blocking, synchronization, streams misuse, collections complexity, I/O, GC.
- Build/tooling: Maven/Gradle config, toolchains, dependency mediation, test runner, packaging.

Ask for or inspect:

- Java version and vendor (`java --version`).
- Full error message and stack trace.
- Minimal code path.
- Build file and test command.
- Expected versus actual behavior.

When editing a repository, run a targeted compile/test command after the fix.

Use `scripts/java_project_info.py <project-root> --pretty` to collect version hints before making version-specific claims or recommending APIs.

Use `scripts/java_version_consistency.py <project-root>` when Maven, Gradle, `.java-version`, `.sdkmanrc`, Docker, CI, or local toolchain clues point to different Java versions.

Use `scripts/java_feature_compat.py <topic> --version <java-version>` before recommending modern Java features to projects with a declared source, target, release, or runtime baseline.

Use `scripts/java_jdk_tool.py <tool-or-task>` before recommending JDK command-line options or diagnostic collection with `java`, `javac`, `jar`, `javadoc`, `jshell`, `jdeps`, `jdeprscan`, `jlink`, `jpackage`, `jcmd`, or `jfr`.

Use `scripts/java_jvm_option.py <option-area-or-alias>` before recommending JVM launcher flags for heap sizing, GC selection/logging, preview features, module access, assertions/properties, diagnostics, or virtual-thread diagnostics.

Use `scripts/java_language_rule.py <rule-or-alias>` before explaining or fixing tricky syntax/type-system behavior such as overload resolution, generic inference, erasure, overriding, initialization order, try-with-resources, lambda capture, records, or pattern-variable scope.

Use `scripts/java_compile_error_triage.py "<javac-diagnostic>"` for common compiler errors such as missing symbols, bad imports/classpaths, incompatible types, overload failures, definite assignment, public type/file name mismatches, and source/release mismatches.

Use `scripts/java_collections_triage.py <issue-or-alias>` for collection choice, equality/hashCode, ordering, concurrent modification, Map update, Optional, and stream pipeline bugs or reviews.

Use `scripts/java_exception_triage.py "<exception-or-stack-trace>"` for common exception first checks and official API links before proposing a bug fix.

Use `scripts/java_io_triage.py <issue-or-alias>` for Path/Files, charsets/text I/O, streams/buffers, resource lifecycle, serialization, sockets, URI/URL, and cross-platform filesystem behavior.

Use `scripts/java_concurrency_triage.py <concern>` for data races, deadlocks, interruption/cancellation, executor lifecycle, virtual-thread suitability, concurrent collections, or atomicity. Collect evidence before changing synchronization or threading design.

Use `scripts/java_verify_commands.py <project-root> --changed-file <path>` to choose the narrowest meaningful compile/test command before running verification.

For performance incidents, run `scripts/java_performance_triage.py <symptom>` before recommending code, JVM flag, GC, or architecture changes. Prioritize collecting JFR, thread dumps, GC evidence, heap evidence, JVM flags, and workload timing.

For Java security questions, run `scripts/java_security_triage.py <risk>` before recommending mitigations. Focus on trust boundaries, untrusted input, resource limits, disclosure paths, and runtime/JDK security configuration.

## Modernization and Migration

First identify the current and target versions. Then check official release notes and JEPs for incompatible changes and new features.

Run `scripts/java_migration_plan.py <source-version> <target-version>` to produce a baseline checklist and official migration links.

Run `scripts/java_module_triage.py <issue-or-alias>` when Java 9+ migration or runtime behavior involves module descriptors, module path/class path boundaries, readability, exports/opens, split packages, services, automatic modules, or jlink images.

Run `scripts/java_deprecation_audit.py --target <target-version> --artifact <jar-or-classes>` after compiling when the migration might involve deprecated APIs, APIs marked for removal, removed APIs, removed tools, or JDK internal APIs.

Prioritize low-risk changes:

- Replace obsolete APIs with supported equivalents.
- Use try-with-resources for closeable resources.
- Use records only when the target version supports them and identity/mutability semantics fit.
- Use switch expressions, pattern matching, text blocks, virtual threads, or sequenced collections only when the target version supports them.
- Preserve public APIs unless the user asks for breaking changes.

For migrations from Java 8/11/17/21 to newer LTS or feature releases, verify:

- Removed Java EE/CORBA modules when migrating from 8 to 11+.
- Strong encapsulation and illegal reflective access issues.
- Deprecated/removed APIs and security provider changes.
- Build plugins, annotation processors, bytecode tools, and test libraries.
- Runtime container image and CI JDK.

## Code Review

Lead with bugs and risks:

- Incorrect equality, ordering, or hashing.
- Unsafe null handling.
- Resource leaks.
- Thread-safety and publication issues.
- Broken generics or raw types.
- Misused streams/optionals.
- Exception swallowing.
- Locale, charset, time zone, and numeric precision problems.
- API/version incompatibility.

Recommend style changes only after correctness issues.

Run `scripts/java_code_review_checklist.py [focus...]` for substantial reviews, especially when security, concurrency, resource management, or Java version compatibility could affect the outcome. Use the generated checks as a source-backed review frame, then report only findings that apply to the code under review.

## Documentation Links

Use `scripts/java_doc_link.py` for quick candidate links, then verify exactness when the answer relies on details.

Examples:

```bash
python java-tutor/scripts/java_doc_link.py api java.util.Optional --version 25
python java-tutor/scripts/java_doc_link.py api 'java.lang.String#toUpperCase()' --version 25
python java-tutor/scripts/java_doc_link.py jls 15 --version 25
python java-tutor/scripts/java_doc_link.py jep 444
python java-tutor/scripts/java_doc_link.py release-notes --version 26
python java-tutor/scripts/java_deprecation_audit.py --target 25 --artifact target/app.jar
python java-tutor/scripts/java_feature_compat.py records --version 11
python java-tutor/scripts/java_feature_compat.py virtual-threads --version 21
python java-tutor/scripts/java_jdk_tool.py javac
python java-tutor/scripts/java_jdk_tool.py 'thread dump' --json
python java-tutor/scripts/java_jvm_option.py xmx
python java-tutor/scripts/java_jvm_option.py 'gc logging' --json
python java-tutor/scripts/java_language_rule.py overload
python java-tutor/scripts/java_language_rule.py 'effectively final' --json
python java-tutor/scripts/java_compile_error_triage.py 'error: cannot find symbol'
python java-tutor/scripts/java_compile_error_triage.py release-source-target --key
python java-tutor/scripts/java_collections_triage.py hashcode
python java-tutor/scripts/java_collections_triage.py 'parallel stream' --json
python java-tutor/scripts/java_concurrency_triage.py data-race
python java-tutor/scripts/java_concurrency_triage.py 'thread pool' --json
python java-tutor/scripts/java_exception_triage.py 'java.lang.NullPointerException'
python java-tutor/scripts/java_io_triage.py utf-8
python java-tutor/scripts/java_io_triage.py 'socket timeout' --json
python java-tutor/scripts/java_learning_path.py beginner
python java-tutor/scripts/java_learning_path.py senior --goal concurrency
python java-tutor/scripts/java_migration_plan.py 8 25
python java-tutor/scripts/java_module_triage.py add-opens
python java-tutor/scripts/java_module_triage.py 'split package' --json
python java-tutor/scripts/java_performance_triage.py gc
python java-tutor/scripts/java_performance_triage.py memory-leak --json
python java-tutor/scripts/java_security_triage.py deserialization
python java-tutor/scripts/java_security_triage.py xxe --json
python java-tutor/scripts/java_project_info.py . --pretty
python java-tutor/scripts/java_version_consistency.py . --json
python java-tutor/scripts/java_topic_links.py virtual-threads
python java-tutor/scripts/java_topic_links.py --list
python java-tutor/scripts/java_verify_commands.py . --changed-file src/test/java/ExampleTest.java
python java-tutor/scripts/java_code_review_checklist.py security concurrency
```
