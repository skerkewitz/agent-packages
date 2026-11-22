#!/usr/bin/env python3
"""Make a new architecture decision record: its ID, its file and its row in the table.

    python3 dev/new_adr.py "The decision, as a sentence"

The ID is 8 characters of Crockford's Base32 (0-9 and A-Z without I, L, O and U): 6 for the
seconds since 2020-01-01 00:00:00 UTC, then 2 for the first 10 bits of the SHA-256 of the
title, so that two records made in the same second still differ. IDs sort by time and last
until 2054. Cite a record as ADR-<ID>.

The file is <dir>/<ID>-<start of the title>.md with the parts of a record to fill in, and the
row goes into the table in the order of the IDs. Paths are relative to the root of the git
repository the current directory is in (the current directory outside git).

Options:
  --table PATH  the table of all records (default docs/ADR.md)
  --dir PATH    the folder of the record files (default docs/adr)
  --at TIME     make the ID for this moment instead of now, such as 2026-11-17T12:00:01Z, for
                a decision taken before records were kept; a time without a zone is UTC

Python 3.9 or later, standard library only. Kept in step with check_adr.py.
"""

import argparse
import datetime
import hashlib
import os
import re
import subprocess
import sys
import unicodedata

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
EPOCH = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
SLUG_LENGTH = 50
TRANSLITERATE = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "æ": "ae", "ø": "oe", "å": "aa"}


def encode(value, width):
    out = ""
    for _ in range(width):
        out = ALPHABET[value % 32] + out
        value //= 32
    return out


def make_id(when, title):
    seconds = int((when - EPOCH).total_seconds())
    if not 0 <= seconds < 32 ** 6:
        raise SystemExit("new_adr: the time must lie between 2020-01-01 and 2054-01-09 UTC")
    digest = hashlib.sha256(title.encode("utf-8")).digest()
    bits = (digest[0] << 8 | digest[1]) >> 6
    return encode(seconds, 6) + encode(bits, 2)


def slug(title):
    text = "".join(TRANSLITERATE.get(c, c) for c in title.lower())
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    out = ""
    for word in re.split(r"[^a-z0-9]+", text):
        if not word:
            continue
        longer = f"{out}-{word}" if out else word
        if len(longer) > SLUG_LENGTH:
            break
        out = longer
    return out


def root():
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        return top.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return os.getcwd()


def parse_time(text):
    when = datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))
    if when.tzinfo is None:
        when = when.replace(tzinfo=datetime.timezone.utc)
    return when.astimezone(datetime.timezone.utc)


def add_row(table, row, new_id):
    """Put the row into the table, before the first row with a later ID."""
    with open(table, encoding="utf-8") as f:
        lines = f.read().split("\n")
    rows = [k for k, line in enumerate(lines) if line.startswith("| ADR-")]
    at = None
    for k in rows:
        if lines[k][6:14] > new_id:
            at = k
            break
    if at is None and rows:
        at = rows[-1] + 1
    if at is None:
        for k, line in enumerate(lines[:-1]):
            if line.startswith("| ID |") and lines[k + 1].startswith("|---"):
                at = k + 2
                break
    if at is None:
        raise SystemExit(f"new_adr: {table} has no table of records (a header starting with \"| ID |\")")
    lines.insert(at, row)
    with open(table, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Make a new architecture decision record.")
    parser.add_argument("title", help="the decision, as a sentence")
    parser.add_argument("--table", default="docs/ADR.md")
    parser.add_argument("--dir", default="docs/adr")
    parser.add_argument("--at", type=parse_time, help="UTC time of the decision, default now")
    args = parser.parse_args()

    title = " ".join(args.title.split())
    if not title or "|" in title:
        raise SystemExit("new_adr: the title is empty or has a |, which would break the table")
    when = args.at or datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    new_id = make_id(when, title)
    name = slug(title)
    if not name:
        raise SystemExit("new_adr: no file name can be made from the title")

    os.chdir(root())
    if not os.path.isfile(args.table):
        raise SystemExit(f"new_adr: {args.table} does not exist; set up the records first")
    os.makedirs(args.dir, exist_ok=True)
    if any(f.startswith(new_id + "-") for f in os.listdir(args.dir)):
        raise SystemExit(f"new_adr: a record ADR-{new_id} exists already; try again in a second")

    path = os.path.join(args.dir, f"{new_id}-{name}.md")
    link = os.path.relpath(path, os.path.dirname(args.table) or ".").replace(os.sep, "/")
    day = (EPOCH + datetime.timedelta(seconds=int((when - EPOCH).total_seconds()))).date().isoformat()
    add_row(args.table, f"| ADR-{new_id} | [{title}]({link}) | Accepted | {day} |", new_id)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# ADR-{new_id}: {title}\n\n**Context.**\n\n**Decision.**\n\n**Alternatives.**\n\n**Consequences.**\n")
    print(f"ADR-{new_id}  {path.replace(os.sep, '/')}")


if __name__ == "__main__":
    sys.exit(main())
