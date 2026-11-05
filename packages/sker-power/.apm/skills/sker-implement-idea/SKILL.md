---
name: sker-implement-idea
description: Implements the decision of a brainstorming summary (a file written by sker-brainstorm, such as docs/brainstorm/<topic>_<date>.md) - builds only what its Decision section says, proves the new behaviour with tests, brings documentation, specifications and requirements in step, runs the project's full verification, and at the end asks whether to move the summary to docs/archive/brainstorm/. Stops and asks through sker-explain-and-solve-problem when the code shows something the summary did not foresee. Use it when the user invokes /sker-implement-idea <file> or asks to implement, build or carry out a brainstorm summary or idea file.
argument-hint: <brainstorm summary file>
---

# Implement an idea: build what a brainstorm decided, nothing more

## Why this skill exists

A brainstorm summary is a decision taken with care: what to build, and just as important, what
not to build yet. The session that implements it usually starts fresh and knows only the file.
Two things go wrong easily: building more than was decided (a postponed idea "while we are at
it"), and settling a fork in silence that the user would have wanted a say in. This skill keeps
the change to the decision and hands every real fork back.

## Input

The argument is the path of the summary, for example
`docs/brainstorm/recursive-classpath_2026-11-01.md`. If none is given, ask for it; do not guess
from the folder. Read the whole file before anything else, then the project's `CLAUDE.md` and the
style guide it names.

## The steps

1. **Build only what the Decision section says.** Read the Problem, Ratings and Open questions
   for context, but the Decision section is the scope. Nothing marked postponed, dropped or kept
   for later is built, not even a part of it. If the Decision section says "open", stop and say
   so: there is nothing decided to build.
2. **Stop and ask on anything the summary did not foresee.** When the code shows a case, a
   conflict or a choice the summary does not settle, do not pick an answer yourself. Use
   `sker-explain-and-solve-problem` to hand it back, and go on only after the user has decided.
   Small choices that the code base already settles by convention (naming, layout) are not forks.
3. **Prove that the new behaviour works.** Every rule or behaviour the decision introduces gets a
   check that fails without the change and passes with it. Normally that is an automated test,
   named after the rule it guards and written in the project's own test style and place. Where
   an automated test is not possible (a UI detail, infrastructure, an outside system), check it
   by hand and write down how you checked it and what you saw.
4. **Bring everything written about the system in step.** The change is not done while any
   text still describes the old behaviour. That covers user and developer documentation, the
   README and help or usage texts, specifications and requirements, architecture notes,
   changelogs, and generated documentation (regenerate it the way the project does). The
   project's `CLAUDE.md` usually says which documents exist; also search the repository for the
   names and terms the change touches, so that nothing is missed. Record the decision where the
   project records decisions, for example as a new ADR that points to the summary at its archive
   path, `docs/archive/brainstorm/<file>`. Never rewrite an existing decision record; add a new
   one that supersedes it.
5. **Prove that nothing else broke.** Run the project's full verification, not only the new
   checks: the build, the whole test suite, and whatever else the project counts as green
   (linters, type checks, static analysis, integration tests, documentation build). `CLAUDE.md`,
   the README or the CI configuration say what that is; if none of them does, ask. Report the
   result as it is: if something fails, show the output and say what you think it means. A
   failure the change did not cause is still reported, not hidden and not fixed in passing.
   Do not commit.
6. **Ask about the summary.** When everything is done, ask the user whether the summary should
   be moved to `docs/archive/brainstorm/`. Move it (with `git mv` if it is tracked) only on a
   yes. On a no, change any reference to it (such as in a new ADR) to the summary's current
   path.

## The report

End with a short report: what was built, how the new behaviour is proven (tests added, manual
checks), the documents, specifications and requirements changed, the result of the full
verification, the forks the user decided along the way, and anything from the Open questions
that is still open.
