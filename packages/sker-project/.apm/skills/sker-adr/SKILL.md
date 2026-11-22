---
name: sker-adr
description: Architecture decision records whose IDs are made from the time and a hash of the title (ADR-<8 characters of Crockford Base32>), so records written on parallel branches never collide and sort by time. A table in docs/ADR.md keeps every record's status, docs/adr/<ID>-<slug>.md holds one record each, new_adr.py makes the ID, file and row, check_adr.py checks table, files and every citation. Use it when a project has such a docs/ADR.md, when the user has taken a decision worth recording, when a record has to be written, superseded, amended or cited, when the user asks to set up decision records in a project or to move numbered ADRs to these IDs, or invokes /sker-adr.
---

# Decision records with time-and-title IDs

Numbered records (ADR 1, 2, 3) break as soon as several branches or agent sessions work at once:
two of them write a record, both take the next number, and the clash shows only when the second
pull request is merged. Then a file, a row and every citation in that branch have to be
renumbered. This scheme gives each record an ID that needs nobody else:

- 8 characters of Crockford's Base32 (`0-9` and `A-Z` without I, L, O and U), so it survives
  case-insensitive file systems and is hard to mistype;
- the first 6 are the seconds since 2020-01-01 00:00 UTC when the record was made, which lasts
  until 2054 and makes IDs sort by time;
- the last 2 are the first 10 bits of the SHA-256 of the title, so that two records made in the
  same second still differ. The title is hashed once; a later change of the title keeps the ID.

A record is cited as `ADR-<ID>`. Its file is `docs/adr/<ID>-<start of the title>.md` and starts
with `# ADR-<ID>: Title`. The table in `docs/ADR.md` lists every record in the order of the IDs,
with its status and the day of its ID in UTC.

The scripts are in this skill's folder, next to this file: `scripts/new_adr.py` and
`scripts/check_adr.py` (Python 3.9+, standard library only). A project that uses the scheme has
its own copies, usually in `dev/`, so that its CI and people without this skill can run them.
Use the project's copies. Some projects have their own variants (superdevkit has
`dev/new_adr.sh` and a Java test); where the project's CLAUDE.md names other paths or tools,
it wins.

## When a decision gets a record

A record answers the question a later reader will ask: why is it like this? Write one for a
decision with consequences beyond the change at hand: architecture, a tool or library, a workflow
rule, a trade-off that costs something. A bug fix or anything the code explains by itself does
not need one.

Only decisions get records. An open question stays in the roadmap, an issue or the document of
its subject, and becomes a record when it is decided. A decision of this weight is the user's to
take (hand it back with `sker-explain-and-solve-problem` where that skill is installed); once
they have taken it, write the record as part of the same change, and say so in the pull request.
Record the reasons they gave. Don't invent better ones.

One record holds one decision. Several rules that belong together may share it.

## Writing a record

1. From the project's root: `python3 dev/new_adr.py "The decision, as a sentence"`. It prints
   the ID and the file. The title states the decision ("Every change goes through a pull request
   into develop"), not the topic ("Branching"), and has no `|`.
2. Fill in the parts the script wrote:
   - **Context.** The situation and what forced a decision. Facts and numbers where there are
     some.
   - **Decision.** What was decided, concretely enough to check against. A list is fine when
     there are several rules.
   - **Alternatives.** What was weighed and why it lost. Delete the heading if nothing was.
   - **Consequences.** What follows, the costs too: what changes in code, docs or workflow,
     what becomes harder.
3. Cite related records by ID. If the new record changes an older one, change the status of
   both in the table (below). Never edit the text of the older record.
4. Run `python3 dev/check_adr.py`.
5. Commit the record with the change it is about.

Once a record is merged, its text stays as it is. A decision that is changed or reversed gets a
new record.

## Status

The table holds the status, never the record. A status is `Accepted` or `Superseded`, followed
by any number of `; <relation> ADR-<ID>, ADR-<ID>` clauses. The relations are `amends`,
`amended by`, `supersedes`, `superseded by` and `superseded in part by`. When B replaces A:

| Record | Status |
|---|---|
| A | `Superseded; superseded by ADR-<B>` |
| B | `Accepted; supersedes ADR-<A>` |

When B changes part of A, A becomes `Accepted; amended by ADR-<B>` and B `Accepted; amends
ADR-<A>`; when B replaces only part of A, A becomes `Accepted; superseded in part by ADR-<B>`.
Clauses add up: `Accepted; amends ADR-<A>; amended by ADR-<C>`.

## Citing

Cite a record as `ADR-<ID>` everywhere: docs, code comments, commit messages, pull requests. In
Markdown docs, link to the file where a reader would want to follow it. A record of another
project gets the project's name in front, as in "superdevkit's ADR-6FCBBNSH"; the check skips
those. IDs of one day share their first 4 or 5 characters, so copy an ID rather than typing it.

## Checking

`python3 dev/check_adr.py` checks the format of the rows and file names, that table and files
agree, that each ID decodes to the date of its row, the order of the table, headings, parts,
statuses, and that every `ADR-<ID>` cited in the repository's text files exists. It exits with 1
and lists each problem. `--table` and `--dir` set other paths; `--skip <path>` leaves vendored
or generated files out of the citation check. It belongs in the project's build or CI.

Two branches that each add a record both append a row, and the second merge conflicts there.
Keep both rows, in the order of their IDs.

## Setting up a project

Do this only when the user asks for it.

1. Look for existing records first. If the project has numbered ADRs or another layout, stop
   and agree with the user whether to migrate (below) or to leave them.
2. Agree on the paths. The defaults are `docs/ADR.md`, `docs/adr/` and the scripts in `dev/`;
   follow the project's layout if it has a folder for such scripts already, and pass
   `--table`/`--dir` or change the defaults at the top of the copies if the records go
   elsewhere.
3. Copy `scripts/new_adr.py` and `scripts/check_adr.py` from this skill into the project and
   `templates/ADR.md` to `docs/ADR.md`. Adjust the template's first paragraph and paths to the
   project.
4. Make the first record, about this scheme: `python3 dev/new_adr.py "Decisions are recorded as
   ADRs with IDs made from the time and the title"`. Its context is why the project keeps
   records and why numbers would collide; fill it from what the user said.
5. Run `check_adr.py` in the project's verification, the way the project already runs checks:
   a CI step, a test that calls it, a make, npm or Gradle task. Ask if there is no obvious place.
6. Add a paragraph to the project's CLAUDE.md (or AGENTS.md), adapted to its paths:

   > Why a decision was taken is in `docs/ADR.md` (the table of all records with their status)
   > and `docs/adr/<ID>-<start-of-title>.md` (one file per record: `# ADR-<ID>: Title`, then
   > **Context.**, **Decision.**, **Alternatives.** where there were any, **Consequences.**).
   > `python3 dev/new_adr.py "Title"` makes the ID, the file and the row. A decision made or
   > changed is a new record; never edit an existing one, change the status of the records it
   > supersedes or amends in the table instead. Cite records by ID (`ADR-<ID>`). An open
   > question becomes a record only when it is decided. `python3 dev/check_adr.py` checks
   > table, files and citations.

7. Commit all of it as one change.

The project's scripts are copies. When this skill's scripts change, compare them and update
the copies on purpose. Checks only one project needs go into a test of its own, not into the
copy of `check_adr.py`.

## Moving numbered records to IDs

With the user's go-ahead only, since every citation changes:

1. Give each record an ID for the day it was decided at 12:00 UTC plus its former number in
   seconds, so records of one day keep their order: `python3 dev/new_adr.py --at
   2026-11-17T12:00:06Z "Title of record 6"`. Move its text into the new file and delete the
   old one.
2. Rewrite every citation of the old numbers in the repository, inside the records too. This is
   the one change made to existing records, and it changes no content.
3. Keep a table from the former numbers to the IDs in `docs/ADR.md`, for commit messages, pull
   requests and other projects that cite a record by number.
4. Run `check_adr.py`, then search for leftovers such as "ADR 6", "record 6" or "ADR-006".
