# Architecture decision records

Decisions taken for this project, oldest first. Each record is a file of its own in `docs/adr/`,
named by its ID and the start of its title, and states the context, the decision, the
alternatives weighed where there were any, and what follows from it. To change a decision, add a
new record that supersedes or amends the old one instead of editing it, and change the status of
the old one in this table. The status of a record is kept here only, so that an old record need
not be edited when a later one changes it.

A record's ID is 8 characters of Crockford's Base32, the digits and the capital letters without
I, L, O and U: 6 for the moment it was made, in seconds since 2020-01-01 00:00 UTC, and 2 for a
hash of its title. Records are cited by ID, as `ADR-<ID>`. The IDs sort by time, and so does this
table; the date of a row is the day of its ID in UTC. Records written on different branches at
the same time do not collide.

`python3 dev/new_adr.py "Title"` makes the ID, the file and the row. `python3 dev/check_adr.py`
checks that the table and the files agree and that every record cited exists.

| ID | Decision | Status | Date |
|---|---|---|---|
