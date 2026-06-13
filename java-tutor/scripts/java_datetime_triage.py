#!/usr/bin/env python3
"""Triage Java date/time issues with official java.time and legacy API links."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


DEFAULT_VERSION = "25"


@dataclass(frozen=True)
class DateTimeIssue:
    key: str
    title: str
    aliases: tuple[str, ...]
    first_checks: tuple[str, ...]
    fixes_to_consider: tuple[str, ...]
    pitfalls: tuple[str, ...]
    docs: tuple[str, ...]


def api(path: str, version: str = DEFAULT_VERSION) -> str:
    return f"https://docs.oracle.com/en/java/javase/{version}/docs/api/java.base/{path}"


def issues(version: str = DEFAULT_VERSION) -> tuple[DateTimeIssue, ...]:
    package_summary = api("java/time/package-summary.html", version)
    instant = api("java/time/Instant.html", version)
    local_date_time = api("java/time/LocalDateTime.html", version)
    zoned_date_time = api("java/time/ZonedDateTime.html", version)
    zone_id = api("java/time/ZoneId.html", version)
    zone_rules = api("java/time/zone/ZoneRules.html", version)
    formatter = api("java/time/format/DateTimeFormatter.html", version)
    parse_exception = api("java/time/format/DateTimeParseException.html", version)
    duration = api("java/time/Duration.html", version)
    period = api("java/time/Period.html", version)
    chrono_unit = api("java/time/temporal/ChronoUnit.html", version)
    legacy_date = api("java/util/Date.html", version)
    calendar = api("java/util/Calendar.html", version)
    time_zone = api("java/util/TimeZone.html", version)
    simple_date_format = api("java/text/SimpleDateFormat.html", version)
    clock = api("java/time/Clock.html", version)
    offset_date_time = api("java/time/OffsetDateTime.html", version)
    zone_offset = api("java/time/ZoneOffset.html", version)
    return (
        DateTimeIssue(
            key="instant-vs-local",
            title="Instant, LocalDateTime, and point-in-time versus wall-clock values",
            aliases=("instant", "localdatetime", "timestamp", "utc", "wall clock", "local time"),
            first_checks=(
                "Decide whether the value represents a point on the time-line or a local human date/time.",
                "Identify the zone or offset used at every external boundary: database, API, UI, logs, and tests.",
                "Check whether ordering, equality, and persistence need UTC instants or local calendar values.",
            ),
            fixes_to_consider=(
                "Use Instant for machine timestamps and audit/event ordering.",
                "Use LocalDate, LocalTime, or LocalDateTime only when a zone-independent local value is the contract.",
                "Convert between local date-times and instants only with an explicit ZoneId or ZoneOffset.",
            ),
            pitfalls=(
                "Treating LocalDateTime as UTC without storing or applying a zone.",
                "Letting the system default time zone silently change persisted or serialized values.",
                "Using string timestamps without documenting the zone/offset convention.",
            ),
            docs=(package_summary, instant, local_date_time, zoned_date_time),
        ),
        DateTimeIssue(
            key="time-zones",
            title="Time zones, ZoneId, ZoneRules, daylight-saving gaps and overlaps",
            aliases=("zoneid", "timezone", "time zone", "dst", "daylight saving", "zoneddatetime"),
            first_checks=(
                "Capture the exact ZoneId, input local date/time, and expected instant or displayed value.",
                "Check whether the local date/time falls in a daylight-saving gap or overlap for that zone.",
                "Distinguish a region-based ZoneId from a fixed numeric offset.",
            ),
            fixes_to_consider=(
                "Use region-based ZoneId values such as Europe/Paris when future civil-time rules matter.",
                "Use ZonedDateTime when local calendar behavior must be resolved through zone rules.",
                "Make gap/overlap handling explicit in tests and conversion code.",
            ),
            pitfalls=(
                "Assuming every local time exists exactly once in every zone.",
                "Using a fixed offset for future appointments that should follow civil time-zone rules.",
                "Relying on defaults that differ between laptops, containers, and production hosts.",
            ),
            docs=(zone_id, zone_rules, zoned_date_time),
        ),
        DateTimeIssue(
            key="format-parse",
            title="DateTimeFormatter patterns, parsing, locales, and resolver behavior",
            aliases=("datetimeformatter", "parse", "format", "pattern", "locale", "date parse"),
            first_checks=(
                "Capture the exact input text, formatter pattern, locale, zone/offset, and exception message.",
                "Check pattern letters carefully, especially year/week-year, month/minute, and zone symbols.",
                "Identify whether parsing should be strict, smart, or lenient for invalid dates.",
            ),
            fixes_to_consider=(
                "Use predefined ISO formatters for ISO-8601 data instead of custom patterns.",
                "Pass an explicit Locale for user-facing text or localized month/day names.",
                "Keep formatting/parsing boundaries separate from domain date/time calculations.",
            ),
            pitfalls=(
                "Using YYYY when yyyy was intended in pattern-based formatting.",
                "Parsing localized text with the wrong default locale.",
                "Assuming a formatter adds missing zone or offset information by itself.",
            ),
            docs=(formatter, parse_exception, zone_id),
        ),
        DateTimeIssue(
            key="duration-period",
            title="Duration, Period, elapsed time, and calendar date arithmetic",
            aliases=("duration", "period", "elapsed", "date math", "plus days", "between"),
            first_checks=(
                "Decide whether the operation is elapsed time in seconds/nanos or calendar movement in dates.",
                "Check whether daylight-saving transitions, month length, leap years, or end-of-month rules apply.",
                "Identify whether the calculation should happen on Instant, LocalDate, or ZonedDateTime values.",
            ),
            fixes_to_consider=(
                "Use Duration for elapsed machine time.",
                "Use Period for date-based amounts measured in years, months, and days.",
                "Test arithmetic around DST boundaries and month ends when business rules depend on civil time.",
            ),
            pitfalls=(
                "Expecting one day to always mean exactly 24 civil-clock hours in every zone.",
                "Using Duration where month and year calendar rules are required.",
                "Ignoring truncation or unit support when using ChronoUnit between temporal values.",
            ),
            docs=(duration, period, chrono_unit, zoned_date_time),
        ),
        DateTimeIssue(
            key="legacy-interop",
            title="Interop with Date, Calendar, TimeZone, and SimpleDateFormat",
            aliases=("date", "calendar", "simpledateformat", "java.util.date", "legacy time", "timezone legacy"),
            first_checks=(
                "Identify the legacy API boundary and convert to java.time at the edge when possible.",
                "Check mutability, thread-safety, default time zone, and lenient parsing behavior.",
                "Confirm whether the legacy type stores an instant, a calendar view, or formatting state.",
            ),
            fixes_to_consider=(
                "Convert Date to Instant and back only at compatibility boundaries.",
                "Prefer DateTimeFormatter over SimpleDateFormat for new formatting/parsing code.",
                "Avoid sharing mutable legacy date/time formatter or calendar instances across threads.",
            ),
            pitfalls=(
                "Assuming Date has no time zone confusion just because it prints using the default zone.",
                "Sharing SimpleDateFormat between threads.",
                "Letting Calendar leniency hide invalid user input.",
            ),
            docs=(legacy_date, calendar, time_zone, simple_date_format, instant, formatter),
        ),
        DateTimeIssue(
            key="clock-testing",
            title="Clock, now(), deterministic tests, and time-dependent code",
            aliases=("clock", "now", "test time", "flaky time", "fixed clock", "time test"),
            first_checks=(
                "Find every direct call to now(), currentTimeMillis(), or default-zone time creation.",
                "Identify whether code needs wall-clock time, elapsed time, or a test-controlled clock.",
                "Check whether tests fail around midnight, DST changes, leap years, or slow CI machines.",
            ),
            fixes_to_consider=(
                "Inject Clock into services that need the current date/time.",
                "Use fixed or offset clocks in tests instead of sleeping.",
                "Keep elapsed-time measurement separate from calendar date/time decisions.",
            ),
            pitfalls=(
                "Scattering now() calls so one operation observes multiple inconsistent times.",
                "Sleeping in tests to prove time passed.",
                "Assuming the system default zone is stable in every runtime environment.",
            ),
            docs=(clock, instant, duration, zone_id),
        ),
        DateTimeIssue(
            key="offset-zone",
            title="OffsetDateTime, ZoneOffset, and offset versus time-zone semantics",
            aliases=("offsetdatetime", "offset", "zone offset", "offset time", "zoned vs offset"),
            first_checks=(
                "Decide whether the value needs only an offset from UTC or full region time-zone rules.",
                "Check whether the value describes a past instant, a future appointment, or a wire protocol field.",
                "Confirm whether downstream systems expect offset-only, UTC instant, or region-zone data.",
            ),
            fixes_to_consider=(
                "Use OffsetDateTime for offset-bearing wire values when region rules are not needed.",
                "Use ZonedDateTime with a region ZoneId for future civil-time scheduling.",
                "Store Instant plus region ZoneId when both ordering and future local display matter.",
            ),
            pitfalls=(
                "Treating an offset such as -07:00 as a full time zone.",
                "Losing future daylight-saving behavior by persisting only an offset.",
                "Mixing offset and zone values without documenting the boundary contract.",
            ),
            docs=(offset_date_time, zone_offset, zoned_date_time, zone_id),
        ),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", "-").split())


def issue_index(version: str = DEFAULT_VERSION) -> dict[str, DateTimeIssue]:
    index: dict[str, DateTimeIssue] = {}
    for issue in issues(version):
        index[normalize(issue.key)] = issue
        index[normalize(issue.title)] = issue
        for alias in issue.aliases:
            index[normalize(alias)] = issue
    return index


def find_issue(query: str, version: str = DEFAULT_VERSION) -> DateTimeIssue:
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
        raise ValueError(f"ambiguous date/time issue {query!r}; choose one of: {options}")
    available = ", ".join(issue.key for issue in issues(version))
    raise ValueError(f"unknown date/time issue {query!r}; available issues: {available}")


def official_urls(selected: Iterable[DateTimeIssue]) -> tuple[str, ...]:
    urls: list[str] = []
    for issue in selected:
        urls.extend(issue.docs)
    return tuple(dict.fromkeys(urls))


def render_text(issue: DateTimeIssue) -> str:
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
    parser.add_argument("issue", nargs="?", help="Date/time issue key or alias")
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
