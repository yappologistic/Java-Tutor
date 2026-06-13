# Java Official Source Map

Use this file to choose official documentation sources. Verify current release facts by browsing official sources when the answer depends on "latest", support status, preview/incubator status, security updates, licensing, or release dates.

## Release Baseline Checked

Last checked: 2026-06-13.

The project verifier's `--check-links` mode checks these release facts against official Oracle pages.

Official sources show:

- Oracle Java downloads page: JDK 26 is the latest Java SE platform release; JDK 25 is the latest LTS; JDK 21 is the previous LTS.
- Oracle Java SE documentation index lists current documentation sets for JDK 26, JDK 25, JDK 21, JDK 17, JDK 11, and JDK 8.
- OpenJDK JDK 25 page states JDK 25 reached General Availability on 2025-09-16.
- JDK 26 release notes state JDK 26 was released on 2026-03-17, with JDK 26.0.1 released on 2026-04-21.

## Primary Sources

| Need | Preferred official source |
| --- | --- |
| Current Java SE docs index | `https://docs.oracle.com/en/java/javase/` |
| Current downloads and LTS label | `https://www.oracle.com/java/technologies/downloads/` |
| Java SE API for version N | `https://docs.oracle.com/en/java/javase/N/docs/api/` |
| JDK N guides | `https://docs.oracle.com/en/java/javase/N/` |
| JDK N migration guide | `https://docs.oracle.com/en/java/javase/N/migrate/index.html` |
| JDK release notes index | `https://www.oracle.com/java/technologies/javase/jdk-relnotes-index.html` |
| JDK 26 release notes | `https://www.oracle.com/java/technologies/javase/26all-relnotes.html` |
| Secure Java coding | `https://www.oracle.com/java/technologies/javase/seccodeguide.html` |
| Java SE security guide | `https://docs.oracle.com/en/java/javase/25/security/index.html` |
| Java language rules | `https://docs.oracle.com/javase/specs/jls/se25/html/index.html` or matching version |
| JVM rules | `https://docs.oracle.com/javase/specs/jvms/se25/html/index.html` or matching version |
| Java SE specifications index | `https://docs.oracle.com/javase/specs/` |
| JEP index | `https://openjdk.org/jeps/0` |
| Specific JEP | `https://openjdk.org/jeps/<number>` |
| OpenJDK release project | `https://openjdk.org/projects/jdk/<version>/` |
| Beginner learning | `https://dev.java/learn/` and `https://docs.oracle.com/javase/tutorial/` |

## Source Selection

Use API docs for class, interface, enum, annotation, method, constructor, exception, module, or package behavior. Link to the exact version used by the project.

Use the JLS for language behavior: overload resolution, generics, var, lambdas, records, sealed classes, pattern matching, definite assignment, initialization order, exceptions, annotations, switch, numeric promotion, and the memory model.

Use the JVMS for class-file format, bytecode verification, class loading/linking/initialization, operand stack behavior, invocation instructions, and JVM startup/execution semantics.

Use JEPs for feature history and rationale. JEPs are not a substitute for the final JLS/JVMS/API once a feature is permanent.

Use release notes for removed APIs, deprecated APIs, behavior changes, security/provider changes, tools changes, compatibility notes, and known issues.

Use Oracle JDK Migration Guides for version-to-version upgrade planning, then cross-check release notes for exact removed/deprecated APIs and compatibility changes.

Use dev.java for modern learning paths and Oracle Tutorials for beginner examples. Mention that some tutorials are older when a lesson predates modern language features.

## Version Policy

When a project declares `--release`, `sourceCompatibility`, `targetCompatibility`, Maven compiler `release`, toolchains, or CI JDK versions, follow that version.

If a library or framework constrains Java compatibility, do not recommend APIs newer than that baseline.

If no version is known:

- For beginner learning, prefer modern LTS Java and clearly state the assumed version.
- For production recommendations, prefer latest LTS unless the user asks for latest features.
- For "latest Java" questions, browse official sources first.

## Common Deep Links

Replace `N` with the selected version:

- API root: `https://docs.oracle.com/en/java/javase/N/docs/api/`
- `java.lang.String`: `https://docs.oracle.com/en/java/javase/N/docs/api/java.base/java/lang/String.html`
- `java.util.List`: `https://docs.oracle.com/en/java/javase/N/docs/api/java.base/java/util/List.html`
- `java.util.Optional`: `https://docs.oracle.com/en/java/javase/N/docs/api/java.base/java/util/Optional.html`
- `java.util.stream.Stream`: `https://docs.oracle.com/en/java/javase/N/docs/api/java.base/java/util/stream/Stream.html`
- `java.util.concurrent`: `https://docs.oracle.com/en/java/javase/N/docs/api/java.base/java/util/concurrent/package-summary.html`
- Java launcher: `https://docs.oracle.com/en/java/javase/N/docs/specs/man/java.html`
- JShell: `https://docs.oracle.com/en/java/javase/N/jshell/`

For common Java topics, prefer `scripts/java_topic_links.py <topic>` to get curated official links plus minimum Java version and feature status.

## Accuracy Checklist

Before finalizing a substantial Java answer:

- Confirm the Java/JDK version.
- Check whether the feature is final, preview, incubator, deprecated, removed, or vendor-specific.
- Prefer exact API/JLS/JVMS/JEP/release-note links over broad pages.
- Avoid claims about "latest" without official verification.
- Separate Java SE behavior from framework behavior such as Spring, Jakarta EE, Android, Kotlin, Maven, or Gradle.
