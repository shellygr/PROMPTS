#!/usr/bin/env python3
"""Fetch all employee information from the Shapes / DreamTeam-V1 GraphQL API and
write it to a single combined markdown file.

READ-ONLY: this script only issues GraphQL `query` operations. It never calls a
mutation (createEmployees / terminateEmployees / attendance writes / chat), so it
cannot modify anything in the HR system.

Setup:
    pip install -r requirements.txt        # requests + python-dotenv

Config (.env in the working directory):
    SHAPES_REFRESH_TOKEN=<token>            # required (exchanged for an access token)
    SHAPES_API_KEY=<token>                  # optional: a ready access token, skips the exchange
    SHAPES_API_URL=https://api.shapes.co/v1 # optional override

Usage:
    python fetch_employees.py [--out employees.md]

The token is loaded via dotenv from the environment; the .env file is never read
directly by this script.
"""

import argparse
import calendar
import json
import sys
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
import os

DEFAULT_URL = "https://api.shapes.co/v1"
HTTP_TIMEOUT = 60  # seconds


# --------------------------------------------------------------------------- #
# GraphQL client
# --------------------------------------------------------------------------- #
class GraphQLError(RuntimeError):
    """A GraphQL response that carried no usable `data`."""


def exchange_refresh_token(url, refresh_token):
    """Exchange a refresh token for a short-lived access token via the
    refreshToken mutation. The refresh token goes in the Refresh-Token header."""
    resp = requests.post(
        url,
        json={"query": REFRESH_M},
        headers={
            "Refresh-Token": refresh_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        timeout=HTTP_TIMEOUT,
    )
    if resp.status_code >= 400:
        raise GraphQLError(
            f"token exchange failed: HTTP {resp.status_code} from {url}\n{resp.text[:1000]}"
        )
    body = resp.json()
    if body.get("errors"):
        raise GraphQLError("token exchange failed:\n" + json.dumps(body["errors"], indent=2))
    access = ((body.get("data") or {}).get("refreshToken") or {}).get("accessToken")
    if not access:
        raise GraphQLError(f"token exchange returned no accessToken: {body}")
    return access


def _is_unauthorized(errors):
    """True if any GraphQL error is a 401/UNAUTHORIZED (e.g. an expired JWT)."""
    for e in errors or []:
        ext = e.get("extensions") or {}
        if ext.get("statusCode") == 401 or ext.get("code") == "UNAUTHORIZED":
            return True
    return False


def make_client(url, token, refresh_token=None):
    """Return a `gql(query, variables)` callable bound to this endpoint.

    If a `refresh_token` is supplied, an expiring access token is transparently
    re-exchanged on a 401 and the request is retried once."""
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )

    def _refresh():
        if not refresh_token:
            return False
        print("  ! access token rejected (401); re-exchanging refresh token ...", file=sys.stderr)
        new_token = exchange_refresh_token(url, refresh_token)
        session.headers["Authorization"] = f"Bearer {new_token}"
        return True

    def gql(query, variables=None, _retried=False):
        resp = session.post(
            url,
            json={"query": query, "variables": variables or {}},
            timeout=HTTP_TIMEOUT,
        )
        # Auth failure can surface at the HTTP layer ...
        if resp.status_code >= 400:
            if resp.status_code == 401 and not _retried and _refresh():
                return gql(query, variables, _retried=True)
            raise GraphQLError(f"HTTP {resp.status_code} from {url}\n{resp.text[:1000]}")

        body = resp.json()
        errors = body.get("errors")
        data = body.get("data")

        # ... or as a GraphQL error with a 401 extension (e.g. "jwt expired").
        if errors and _is_unauthorized(errors) and not _retried and _refresh():
            return gql(query, variables, _retried=True)

        if errors and data is None:
            # Total failure: no data came back at all.
            raise GraphQLError(json.dumps(errors, indent=2))
        if errors:
            # Partial result (e.g. an Admin-only field nulled out). Keep going
            # but tell the user which fields were dropped.
            paths = ["/".join(str(p) for p in (e.get("path") or [])) for e in errors]
            print(
                f"  ! partial result, {len(errors)} field error(s): "
                + ", ".join(p for p in paths if p),
                file=sys.stderr,
            )
        return data, errors

    return gql


# --------------------------------------------------------------------------- #
# Queries
# --------------------------------------------------------------------------- #
# Auth bootstrap: trade the refresh token (sent in the Refresh-Token header) for
# a short-lived access token. This is the only mutation used, and only to
# authenticate — it touches no employee data.
REFRESH_M = "mutation { refreshToken { accessToken refreshToken } }"

ME_Q = "query { me { id email } }"

# workStatus is Admin-only; templated so we can drop it on a permission error.
EMPLOYEES_Q = """
query {{
  employees {{
    id
    firstName
    lastName
    email
    {work_status}
    employeeFieldValues {{
      id
      employeeFieldTypeId
      textValue
      fieldValue
      effectiveDate
      updatedAt
      employeeFieldType {{ id fieldName fieldType context }}
    }}
  }}
}}
"""

ANNIVERSARIES_Q = """
query {
  employeeAnniversaries {
    employeeId
    type
    month
    day
    validFrom
  }
}
"""

REASONS_Q = """
query {
  timeAwayReasons {
    id
    type
    name
    position
    status
    isPrivate
  }
}
"""

BOOKINGS_Q = """
query {
  timeAwayBookings {
    id
    employeeId
    timeAwayReasonId
    fromDate
    toDate
    bookingStatus
    bookedByEmployeeId
    explanation
    bookingStatusUpdatedAt
  }
}
"""


def fetch_employees(gql):
    """Fetch employees with their nested field values, degrading gracefully if
    the token lacks permission to read the Admin-only `workStatus` field."""
    data, errors = gql(EMPLOYEES_Q.format(work_status="workStatus"))
    if errors and any("workStatus" in (str(p) for p in (e.get("path") or [])) for e in errors):
        print("  ! retrying employees query without Admin-only workStatus", file=sys.stderr)
        data, _ = gql(EMPLOYEES_Q.format(work_status=""))
    return (data or {}).get("employees") or []


# --------------------------------------------------------------------------- #
# Value rendering
# --------------------------------------------------------------------------- #
def flatten_richtext(node):
    """Pull plain text out of a Slate-style rich-text JSON document."""
    out = []

    def walk(n):
        if isinstance(n, dict):
            if isinstance(n.get("text"), str):
                out.append(n["text"])
            for child in n.get("children", []) or []:
                walk(child)
        elif isinstance(n, list):
            for child in n:
                walk(child)

    walk(node)
    return " ".join(t for t in out if t).strip()


def render_field_value(fv):
    """Human-readable rendering of one EmployeeFieldValue.

    Prefers the server-flattened `textValue`; falls back to interpreting the
    raw `fieldValue` JSON by shape (country struct, list, scalar, ...)."""
    text = fv.get("textValue")
    if text not in (None, ""):
        return str(text)

    raw = fv.get("fieldValue")
    if raw is None:
        return ""
    if isinstance(raw, dict):
        # country kind stores {countryCode, countryName}
        if "countryName" in raw:
            code = raw.get("countryCode")
            return f"{raw['countryName']}" + (f" ({code})" if code else "")
        return json.dumps(raw, ensure_ascii=False)
    if isinstance(raw, list):
        return ", ".join(str(x) for x in raw)
    return str(raw)


def group_fields(field_values):
    """Group an employee's effective-dated field values by field type.

    Each group is sorted oldest→newest so the full history is preserved. Sort
    key prefers effectiveDate, tie-breaks on updatedAt (ISO strings sort
    chronologically). Returns a list of (fieldType, [values]) ordered by
    (context, fieldName)."""
    def vkey(fv):
        return (fv.get("effectiveDate") or "", fv.get("updatedAt") or "")

    by_type = {}
    for fv in field_values:
        by_type.setdefault(fv.get("employeeFieldTypeId"), []).append(fv)

    groups = []
    for vals in by_type.values():
        vals.sort(key=vkey)
        ft = (vals[-1].get("employeeFieldType")) or {}
        groups.append((ft, vals))

    groups.sort(key=lambda g: ((g[0].get("context") or ""), (g[0].get("fieldName") or "")))
    return groups


def render_field_history(vals):
    """Render a field's current value, or its full effective-dated history when
    more than one value exists. `vals` is oldest→newest."""
    if len(vals) == 1:
        return render_field_value(vals[0])
    parts = []
    for fv in vals:
        eff = (fv.get("effectiveDate") or "")[:10]  # date part only
        label = eff if eff else "initial"
        parts.append(f"{label}: {render_field_value(fv)}")
    return " → ".join(parts)


def render_date_part(part):
    """Render a TimeAwayBooking fromDate/toDate JSON: {date, halfDayPart}."""
    if not isinstance(part, dict):
        return str(part) if part else ""
    date = part.get("date") or ""
    half = part.get("halfDayPart")
    return f"{date} ({half})" if half else date


# --------------------------------------------------------------------------- #
# Markdown helpers
# --------------------------------------------------------------------------- #
def cell(value):
    """Escape a value for use inside a markdown table cell."""
    s = "" if value is None else str(value)
    return s.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").strip()


def emp_name(emp):
    return f"{emp.get('firstName', '')} {emp.get('lastName', '')}".strip()


def build_markdown(employees, anniversaries, reasons, bookings, source_url):
    reasons_by_id = {r["id"]: r for r in reasons}
    annis_by_emp = {}
    for a in anniversaries:
        annis_by_emp.setdefault(a["employeeId"], []).append(a)
    bookings_by_emp = {}
    for b in bookings:
        bookings_by_emp.setdefault(b["employeeId"], []).append(b)

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    L = []
    L.append("# Employee directory (Shapes / DreamTeam-V1)")
    L.append("")
    L.append(f"- Generated: {generated}")
    L.append(f"- Source: `{source_url}`")
    L.append(f"- Employees: {len(employees)}")
    L.append(f"- Time-away bookings: {len(bookings)} | Anniversaries: {len(anniversaries)}")
    L.append("")

    # Roster summary --------------------------------------------------------- #
    L.append("## Roster")
    L.append("")
    L.append("| ID | Name | Email | Work status |")
    L.append("| --- | --- | --- | --- |")
    for e in employees:
        L.append(
            f"| {cell(e.get('id'))} | {cell(emp_name(e))} | "
            f"{cell(e.get('email'))} | {cell(e.get('workStatus'))} |"
        )
    L.append("")

    # Per-employee detail ---------------------------------------------------- #
    L.append("## Employees")
    L.append("")
    for e in employees:
        eid = e.get("id")
        L.append(f"### {emp_name(e)}  ·  `{eid}`")
        L.append("")
        L.append(f"- Email: {e.get('email', '')}")
        if e.get("workStatus") is not None:
            L.append(f"- Work status: {e['workStatus']}")
        L.append("")

        groups = group_fields(e.get("employeeFieldValues") or [])
        if groups:
            L.append("| Field | Value |")
            L.append("| --- | --- |")
            for ft, vals in groups:
                L.append(f"| {cell(ft.get('fieldName'))} | {cell(render_field_history(vals))} |")
            L.append("")

        annis = annis_by_emp.get(eid) or []
        if annis:
            L.append("**Anniversaries:**")
            L.append("")
            for a in annis:
                month_name = calendar.month_name[a["month"] + 1]  # month is zero-indexed
                L.append(f"- {a.get('type', '')}: {month_name} {a.get('day')}")
            L.append("")

        bks = bookings_by_emp.get(eid) or []
        if bks:
            L.append("**Time away:**")
            L.append("")
            L.append("| Reason | From | To | Status | Note |")
            L.append("| --- | --- | --- | --- | --- |")
            for b in bks:
                reason = reasons_by_id.get(b.get("timeAwayReasonId"), {})
                note = flatten_richtext(b.get("explanation"))
                L.append(
                    f"| {cell(reason.get('name'))} | {cell(render_date_part(b.get('fromDate')))} | "
                    f"{cell(render_date_part(b.get('toDate')))} | {cell(b.get('bookingStatus'))} | "
                    f"{cell(note)} |"
                )
            L.append("")

    # Reference appendix ----------------------------------------------------- #
    if reasons:
        L.append("## Appendix: time-away reasons")
        L.append("")
        L.append("| ID | Name | Type | Private |")
        L.append("| --- | --- | --- | --- |")
        for r in sorted(reasons, key=lambda r: (r.get("position") or 0)):
            L.append(
                f"| {cell(r.get('id'))} | {cell(r.get('name'))} | "
                f"{cell(r.get('type'))} | {cell(r.get('isPrivate'))} |"
            )
        L.append("")

    return "\n".join(L)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="employees.md", help="output markdown file")
    args = parser.parse_args()

    load_dotenv()
    url = os.environ.get("SHAPES_API_URL", DEFAULT_URL)
    refresh = os.environ.get("SHAPES_REFRESH_TOKEN")

    # Prefer the refresh token: exchange it for a fresh access token. A
    # pre-supplied SHAPES_API_KEY is only used when no refresh token is set
    # (otherwise a stale key would shadow the refresh flow).
    if refresh:
        print("exchanging refresh token for an access token ...")
        token = exchange_refresh_token(url, refresh)
    else:
        token = os.environ.get("SHAPES_API_KEY")
        if not token:
            sys.exit("error: set SHAPES_REFRESH_TOKEN (or SHAPES_API_KEY) in .env")

    gql = make_client(url, token, refresh_token=refresh)

    # Validate the token first.
    data, _ = gql(ME_Q)
    me = (data or {}).get("me") or {}
    print(f"authed as {me.get('email', '<unknown>')} ({url})")

    print("fetching employees + field values ...")
    employees = fetch_employees(gql)
    print(f"  {len(employees)} employees")

    print("fetching anniversaries ...")
    anniversaries = ((gql(ANNIVERSARIES_Q)[0] or {}).get("employeeAnniversaries")) or []
    print(f"  {len(anniversaries)} anniversaries")

    print("fetching time-away reasons ...")
    reasons = ((gql(REASONS_Q)[0] or {}).get("timeAwayReasons")) or []
    print(f"  {len(reasons)} reasons")

    print("fetching time-away bookings ...")
    bookings = ((gql(BOOKINGS_Q)[0] or {}).get("timeAwayBookings")) or []
    print(f"  {len(bookings)} bookings")

    md = build_markdown(employees, anniversaries, reasons, bookings, url)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"wrote {args.out} ({len(md):,} bytes)")


if __name__ == "__main__":
    main()
