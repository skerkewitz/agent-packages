#!/usr/bin/env python3
"""Check the architecture decision records: the table, the files and every citation.

    python3 dev/check_adr.py

Nothing else keeps the table and the record files in step, so this does:

- every row of the table reads | ADR-<ID> | [Title](<dir>/<file>) | Status | YYYY-MM-DD |,
  the rows are in the order of their IDs, and each ID is there once;
- every file in the record folder is <ID>-<start of the title>.md and has its row, every row
  its file, and the row links to it;
- each ID decodes to the date of its row (the day in UTC);
- a record starts with "# ADR-<ID>: Title", the title of its row, and has the parts
  **Context.**, **Decision.** and **Consequences.**, and no status, which the table keeps;
- a status is "Accepted" or "Superseded", optionally followed by "; amends", "; supersedes",
  "; amended by", "; superseded by" or "; superseded in part by" and records that exist;
- every ADR-<ID> cited in a text file of the repository is a record in the table. A record of
  another project is cited with its name in front ("gosu-flint's ADR-6F0R61EZ") and is skipped.

Prints what is wrong and exits with 1, or prints how many records it checked and exits with 0.

Options:
  --table PATH    the table of all records (default docs/ADR.md)
  --dir PATH      the folder of the record files (default docs/adr)
  --skip PREFIX   leave files under this path out of the citation check; can be repeated

Paths are relative to the root of the git repository the current directory is in. In a git
repository the citation check reads the files git tracks or would track; outside one, every
file below the root except hidden folders. Python 3.9 or later, standard library only. Kept in
step with new_adr.py.
"""

import argparse
import datetime
import os
import re
import subprocess
import sys

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
EPOCH = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
ID = "[0-9A-HJKMNP-TV-Z]{8}"
FILE_NAME = re.compile(rf"({ID})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md")
ROW = re.compile(rf"\| ADR-({ID}) \| \[(.+)\]\(([^)]+)\) \| ([^|]+) \| (\d{{4}}-\d{{2}}-\d{{2}}) \|")
HEADING = re.compile(rf"# ADR-({ID}): (.+)")
STATUS = re.compile(
    rf"(Accepted|Superseded)((; (amends|supersedes|amended by|superseded by|superseded in part by)"
    rf" ADR-{ID}(, ADR-{ID})*)*)")
CITED = re.compile(r"\bADR-([0-9A-Za-z]{8})\b")
OTHER_PROJECT = re.compile(r"[\w-]+'s\s+$")
PARTS = ("**Context.**", "**Decision.**", "**Consequences.**")


def made(record_id):
    seconds = 0
    for c in record_id[:6]:
        seconds = seconds * 32 + ALPHABET.index(c)
    return EPOCH + datetime.timedelta(seconds=seconds)


def root():
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        return top.stdout.strip(), True
    except (OSError, subprocess.CalledProcessError):
        return os.getcwd(), False


def documents(in_git):
    if in_git:
        listed = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                                capture_output=True, check=True).stdout.decode("utf-8")
        files = [f for f in listed.split("\0") if f]
    else:
        files = []
        for top, dirs, names in os.walk("."):
            dirs[:] = sorted(d for d in dirs if not d.startswith("."))
            files += [os.path.relpath(os.path.join(top, n)).replace(os.sep, "/") for n in names]
    return sorted(f for f in files if os.path.isfile(f))


def read_text(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        if b"\0" in data:
            return None
        return data.decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def check(table, record_dir, skips, in_git):
    problems = []
    link_prefix = os.path.relpath(record_dir, os.path.dirname(table) or ".").replace(os.sep, "/") + "/"

    rows = []
    with open(table, encoding="utf-8") as f:
        for line in f.read().splitlines():
            if not line.startswith("| ADR-"):
                continue
            m = ROW.fullmatch(line.rstrip())
            if not m:
                problems.append(f"{table}: a row that is not | ADR-<ID> | [Title]({link_prefix}<file>) | Status | Date |: {line}")
                continue
            rows.append((m.group(1), m.group(2), m.group(3), m.group(4).strip(), m.group(5)))

    ids = [r[0] for r in rows]
    if ids != sorted(set(ids)):
        problems.append(f"{table}: the rows are not in the order of their IDs, or an ID is there twice")

    files = {}
    for name in sorted(os.listdir(record_dir)) if os.path.isdir(record_dir) else []:
        m = FILE_NAME.fullmatch(name)
        if not m or len(m.group(2)) > 50:
            problems.append(f"{record_dir}/{name}: not <ID>-<start of the title>.md with at most 50 characters after the ID")
        elif m.group(1) in files:
            problems.append(f"{record_dir}/{name}: a second file for ADR-{m.group(1)}")
        else:
            files[m.group(1)] = name

    known = set(ids)
    for record_id in sorted(set(files) - known):
        problems.append(f"{record_dir}/{files[record_id]}: no row in {table}")
    for record_id, title, link, status, day in rows:
        name = files.get(record_id)
        if name is None:
            problems.append(f"{table}: ADR-{record_id} has no file in {record_dir}")
            continue
        if link != link_prefix + name:
            problems.append(f"{table}: the row of ADR-{record_id} links to {link}, not {link_prefix + name}")
        if made(record_id).date().isoformat() != day:
            problems.append(f"{table}: ADR-{record_id} was made on {made(record_id).date()} UTC, its row says {day}")

        text = read_text(os.path.join(record_dir, name)) or ""
        first = text.split("\n", 1)[0]
        h = HEADING.fullmatch(first.rstrip())
        if not h or h.group(1) != record_id:
            problems.append(f"{record_dir}/{name}: does not start with \"# ADR-{record_id}: Title\"")
        elif h.group(2) != title:
            problems.append(f"{record_dir}/{name}: the title differs from its row in {table}")
        for part in PARTS:
            if part not in text:
                problems.append(f"{record_dir}/{name}: has no {part}")
        if re.search(r"^\**Status[:.]", text, re.MULTILINE):
            problems.append(f"{record_dir}/{name}: has a status; it is kept in {table} only")

        s = STATUS.fullmatch(status)
        if not s:
            problems.append(f"{table}: ADR-{record_id} has the status \"{status}\", not one such as"
                            " \"Accepted; amended by ADR-<ID>\"")
        else:
            for named in re.findall(rf"ADR-({ID})", s.group(2)):
                if named not in known or named == record_id:
                    problems.append(f"{table}: the status of ADR-{record_id} names ADR-{named}")

    for path in documents(in_git):
        if any(path == p or path.startswith(p.rstrip("/") + "/") for p in skips):
            continue
        text = read_text(path)
        if text is None:
            continue
        for m in CITED.finditer(text):
            if m.group(1) in known or OTHER_PROJECT.search(text[max(0, m.start() - 40):m.start()]):
                continue
            line = text.count("\n", 0, m.start()) + 1
            problems.append(f"{path}:{line}: cites ADR-{m.group(1)}, which {table} does not have")

    return problems, len(rows)


def main():
    parser = argparse.ArgumentParser(description="Check the architecture decision records.")
    parser.add_argument("--table", default="docs/ADR.md")
    parser.add_argument("--dir", default="docs/adr")
    parser.add_argument("--skip", action="append", default=[], metavar="PREFIX")
    args = parser.parse_args()

    top, in_git = root()
    os.chdir(top)
    if not os.path.isfile(args.table):
        print(f"check_adr: {args.table} does not exist", file=sys.stderr)
        return 1
    problems, count = check(args.table, args.dir.rstrip("/"), args.skip, in_git)
    for problem in problems:
        print(problem)
    if problems:
        sys.stdout.flush()
        print(f"check_adr: {len(problems)} problem(s) in {count} records", file=sys.stderr)
        return 1
    print(f"check_adr: {count} records, all in order")
    return 0


if __name__ == "__main__":
    sys.exit(main())
