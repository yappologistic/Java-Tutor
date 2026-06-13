#!/usr/bin/env python3
"""Triage JDBC, SQL, transaction, and ResultSet issues with official java.sql links."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class JdbcIssue:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    fixes_to_consider: tuple[str, ...]
    pitfalls: tuple[str, ...]
    docs: tuple[str, ...]


def api(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/java.sql/{path}"


def base_api(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/{path}"


def issues(version: str = DEFAULT_VERSION) -> tuple[JdbcIssue, ...]:
    package_summary = api("java/sql/package-summary.html", version)
    connection = api("java/sql/Connection.html", version)
    datasource = api("javax/sql/DataSource.html", version)
    driver_manager = api("java/sql/DriverManager.html", version)
    statement = api("java/sql/Statement.html", version)
    prepared_statement = api("java/sql/PreparedStatement.html", version)
    callable_statement = api("java/sql/CallableStatement.html", version)
    result_set = api("java/sql/ResultSet.html", version)
    result_set_meta = api("java/sql/ResultSetMetaData.html", version)
    sql_exception = api("java/sql/SQLException.html", version)
    sql_warning = api("java/sql/SQLWarning.html", version)
    batch_update_exception = api("java/sql/BatchUpdateException.html", version)
    sql_timeout_exception = api("java/sql/SQLTimeoutException.html", version)
    sql_integrity_exception = api("java/sql/SQLIntegrityConstraintViolationException.html", version)
    savepoint = api("java/sql/Savepoint.html", version)
    blob = api("java/sql/Blob.html", version)
    clob = api("java/sql/Clob.html", version)
    sql_date = api("java/sql/Date.html", version)
    sql_time = api("java/sql/Time.html", version)
    sql_timestamp = api("java/sql/Timestamp.html", version)
    local_date = base_api("java/time/LocalDate.html", version)
    local_date_time = base_api("java/time/LocalDateTime.html", version)
    instant = base_api("java/time/Instant.html", version)
    return (
        JdbcIssue(
            key="connection-lifecycle",
            title="Connection lifecycle, DataSource, pooling, and resource ownership",
            aliases=("connection", "datasource", "pool", "connection pool", "drivermanager", "leak"),
            first_checks=(
                "Identify who owns each Connection, Statement, ResultSet, and pool lifecycle.",
                "Check whether try-with-resources closes JDBC resources on success and failure paths.",
                "Capture pool size, timeout settings, transaction boundaries, and long-running queries.",
            ),
            fixes_to_consider=(
                "Use DataSource-managed connections in applications instead of DriverManager in hot paths.",
                "Close ResultSet, Statement, and Connection at the narrowest ownership scope.",
                "Tune pool size and timeouts from workload evidence rather than increasing them blindly.",
            ),
            pitfalls=(
                "Returning a lazy stream or iterator after closing the Connection that backs it.",
                "Keeping a transaction open while doing unrelated network or application work.",
                "Treating pooled Connection.close as destructive instead of returning it to the pool.",
            ),
            docs=(package_summary, connection, datasource, driver_manager),
        ),
        JdbcIssue(
            key="prepared-statements",
            title="PreparedStatement parameters, SQL injection boundaries, and generated SQL",
            aliases=("preparedstatement", "prepared statement", "sql injection", "parameter", "bind", "placeholder"),
            first_checks=(
                "Separate SQL identifiers and structure from user-controlled values.",
                "Check that every user-controlled value is bound as a parameter, not concatenated into SQL.",
                "Confirm parameter indexes, SQL types, null handling, and driver-specific generated SQL behavior.",
            ),
            fixes_to_consider=(
                "Use PreparedStatement parameters for values and allow-list identifiers such as table or column names.",
                "Use setObject with an explicit target SQL type when driver inference is ambiguous.",
                "Log SQL templates and parameter summaries without exposing sensitive values.",
            ),
            pitfalls=(
                "Trying to bind table names, column names, or ORDER BY direction as PreparedStatement values.",
                "Building IN lists by string concatenation without validating or binding each value.",
                "Assuming prepared statements alone solve authorization or row-level access problems.",
            ),
            docs=(prepared_statement, statement, base_api("java/lang/String.html", version)),
        ),
        JdbcIssue(
            key="transactions",
            title="Transactions, auto-commit, isolation, rollback, and savepoints",
            aliases=("transaction", "autocommit", "rollback", "commit", "isolation", "savepoint"),
            first_checks=(
                "Identify the transaction owner and whether auto-commit is enabled.",
                "Check isolation level, lock waits, deadlocks, retries, and rollback paths.",
                "Verify that commit or rollback happens exactly once for each transaction boundary.",
            ),
            fixes_to_consider=(
                "Disable auto-commit only inside a clearly scoped transaction owner.",
                "Use try/catch/finally or framework transaction support to guarantee rollback on failure.",
                "Use savepoints only when partial rollback semantics are required and tested.",
            ),
            pitfalls=(
                "Forgetting to restore connection state before returning a pooled connection.",
                "Catching SQLException and continuing after an unknown transaction outcome.",
                "Assuming isolation-level names mean identical behavior across every database engine.",
            ),
            docs=(connection, savepoint, sql_exception),
        ),
        JdbcIssue(
            key="result-sets",
            title="ResultSet cursor, column access, metadata, streaming, and large results",
            aliases=("resultset", "cursor", "metadata", "fetch size", "streaming", "column index"),
            first_checks=(
                "Check cursor movement: next must succeed before reading current row columns.",
                "Identify result size, fetch size, memory behavior, and whether the driver streams or buffers rows.",
                "Verify column labels, indexes, null handling, and type conversions against ResultSetMetaData.",
            ),
            fixes_to_consider=(
                "Use column labels for readability when SQL aliases are stable.",
                "Check wasNull after primitive getters when SQL NULL has distinct meaning.",
                "Set fetch size or use pagination only after confirming database and driver behavior.",
            ),
            pitfalls=(
                "Reading a ResultSet before calling next.",
                "Using primitive getters and losing SQL NULL information.",
                "Assuming fetch size always enables server-side streaming.",
            ),
            docs=(result_set, result_set_meta, statement),
        ),
        JdbcIssue(
            key="batching-generated-keys",
            title="Batch updates, generated keys, update counts, and partial failures",
            aliases=("batch", "execute batch", "generated keys", "update count", "batchupdateexception"),
            first_checks=(
                "Capture batch size, transaction mode, driver rewrite settings, and generated-key expectations.",
                "Check update counts and BatchUpdateException contents after partial failure.",
                "Verify whether generated keys are required for every batch element and supported by the driver.",
            ),
            fixes_to_consider=(
                "Use executeBatch for repeated parameterized statements when driver/database support is appropriate.",
                "Handle partial batch failures explicitly and decide retry/rollback behavior.",
                "Request generated keys only when needed and test the exact driver behavior.",
            ),
            pitfalls=(
                "Assuming a failed batch rolled back without checking transaction mode.",
                "Ignoring update counts and generated-key ordering.",
                "Using huge batches that exceed packet, memory, lock, or timeout limits.",
            ),
            docs=(statement, prepared_statement, batch_update_exception),
        ),
        JdbcIssue(
            key="sql-exceptions",
            title="SQLException chains, SQLState, vendor codes, timeouts, and warnings",
            aliases=("sqlexception", "sqlstate", "vendor code", "timeout", "sqlwarning", "deadlock"),
            first_checks=(
                "Capture SQLState, vendor error code, exception chain, warnings, query timeout, and database logs.",
                "Classify whether the failure is transient, constraint-related, timeout-related, syntax, or connection loss.",
                "Check whether retry is safe for the current transaction and statement idempotency.",
            ),
            fixes_to_consider=(
                "Iterate SQLException chains instead of logging only the top-level message.",
                "Use specific SQLException subclasses when the JDBC driver reports them reliably.",
                "Set query timeouts where the service contract requires bounded waits.",
            ),
            pitfalls=(
                "Retrying non-idempotent statements after an unknown commit outcome.",
                "Ignoring SQLWarning when the database reports truncation or degraded behavior as a warning.",
                "Treating vendor error codes as portable across database engines.",
            ),
            docs=(sql_exception, sql_warning, sql_timeout_exception, sql_integrity_exception),
        ),
        JdbcIssue(
            key="date-time-mapping",
            title="JDBC date/time mapping, java.time, Timestamp, zones, and precision",
            aliases=("timestamp", "date", "time", "localdate", "localdatetime", "instant", "timezone"),
            first_checks=(
                "Identify SQL column type, Java type, database/session time zone, driver version, and precision.",
                "Check whether the value is a date, local date-time, offset/instant, or database-specific timestamp.",
                "Verify truncation, rounding, and zone conversion at read/write boundaries.",
            ),
            fixes_to_consider=(
                "Use JDBC 4.2 java.time mappings when the driver and database support them.",
                "Use LocalDate for SQL DATE and LocalDateTime for zone-free SQL TIMESTAMP semantics.",
                "Document UTC/zone conventions explicitly when persisting instants.",
            ),
            pitfalls=(
                "Assuming java.sql.Timestamp carries full time-zone semantics.",
                "Losing nanosecond precision or offset information at driver/database boundaries.",
                "Letting the JVM or database default time zone silently affect persisted values.",
            ),
            docs=(prepared_statement, result_set, sql_date, sql_time, sql_timestamp, local_date, local_date_time, instant),
        ),
        JdbcIssue(
            key="lob-streaming",
            title="BLOB/CLOB streaming, binary/text data, resource lifetime, and memory use",
            aliases=("blob", "clob", "lob", "binary", "large object", "stream"),
            first_checks=(
                "Identify data size, text versus binary semantics, character encoding, and transaction/resource lifetime.",
                "Check whether the driver streams LOB data or materializes it in memory.",
                "Verify that streams remain valid only while the owning JDBC resources remain open.",
            ),
            fixes_to_consider=(
                "Stream large binary/text data instead of loading it all into arrays or strings.",
                "Keep Connection, Statement, ResultSet, and LOB stream lifetimes aligned.",
                "Use explicit character encodings when converting between bytes and text outside JDBC character APIs.",
            ),
            pitfalls=(
                "Returning an InputStream after closing the ResultSet or Connection that owns it.",
                "Treating binary data as text and corrupting it through charset conversion.",
                "Loading large LOBs into heap memory without limits.",
            ),
            docs=(blob, clob, result_set, prepared_statement),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def issue_index(version: str = DEFAULT_VERSION) -> dict[str, JdbcIssue]:
    index: dict[str, JdbcIssue] = {}
    for issue in issues(version):
        index[normalize(issue.key)] = issue
        index[normalize(issue.title)] = issue
        for alias in issue.aliases:
            index[normalize(alias)] = issue
    return index


def find_issue(query: str, version: str = DEFAULT_VERSION) -> JdbcIssue:
    normalized = normalize(query)
    index = issue_index(version)
    if normalized in index:
        return index[normalized]
    matches = [issue for key, issue in index.items() if normalized in key or key in normalized]
    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    if unique_matches:
        options = ", ".join(issue.key for issue in unique_matches)
        raise ValueError(f"ambiguous JDBC issue {query!r}; choose one of: {options}")
    available = ", ".join(issue.key for issue in issues(version))
    raise ValueError(f"unknown JDBC issue {query!r}; available issues: {available}")


def official_urls(selected: Iterable[JdbcIssue]) -> tuple[str, ...]:
    urls: list[str] = []
    for issue in selected:
        urls.extend(issue.docs)
    return tuple(dict.fromkeys(urls))


def render_text(issue: JdbcIssue) -> str:
    lines = [issue.title, f"Key: {issue.key}", "", "First checks:"]
    lines.extend(f"{index}. {check}" for index, check in enumerate(issue.first_checks, start=1))
    lines.extend(["", "Fixes to consider:"])
    lines.extend(f"- {item}" for item in issue.fixes_to_consider)
    lines.extend(["", "Pitfalls:"])
    lines.extend(f"- {item}" for item in issue.pitfalls)
    lines.extend(["", "Official docs:"])
    lines.extend(f"- {url}" for url in issue.docs)
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("issue", nargs="?", help="JDBC issue key or alias")
    parser.add_argument("--list", action="store_true", help="List known issue keys")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Java SE documentation version")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args(argv)

    if args.list:
        keys = [issue.key for issue in issues(args.version)]
        print(json.dumps(keys, indent=2) if args.json else "\n".join(keys))
        return 0

    if not args.issue:
        parser.error("issue is required unless --list is used")

    try:
        issue = find_issue(args.issue, args.version)
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        payload = asdict(issue)
        payload["official_docs"] = list(issue.docs)
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(issue))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
