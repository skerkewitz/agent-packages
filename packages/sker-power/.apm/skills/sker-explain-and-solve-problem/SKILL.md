---
name: sker-explain-and-solve-problem
description: Hands a decision back to the user properly — explains the problem in plain language, lays out real options tagged by what they cost (dirty quick fix / contained fix / structural change / change the requirement / defer), gives honest pros and cons including whether an upcoming roadmap step makes an option pointless, and closes with one recommendation and the reasoning behind it. Use this skill whenever you hit a fork you should not settle alone — a bug with several plausible fixes, a design choice whose consequences outlive the current task, a tempting workaround, a "patch it or do it properly" moment, a discrepancy between the code and the spec or reference implementation it came from — and whenever the user asks "what are my options", "how should we solve this", "quick fix or do it right", or "what do you suggest". Reach for it proactively, before quietly choosing an approach the user would have wanted a say in: choosing silently is the exact failure this skill exists to prevent.
---

# Explain and Solve Problem — handing a fork back to the user

## Why this skill exists

You are deeper in the problem than the user is. You have read the code, the specs and the docs in the
last ten minutes; they have not, at least not today. That asymmetry is the whole difficulty. A decision
they make without your context is a guess. A decision *you* make without their intent is a quiet
imposition — and the ones that hurt are never the loud ones, they are the small approach choices nobody
was asked about.

So the job is **not to persuade**. It is to transfer enough context that their choice is as informed as
yours would be, then say what you would do and why. They decide.

## When to use this — and when not to

Use it when the fork has consequences that outlive the current task:

- A bug with several plausible fixes at different depths.
- A tempting workaround that would work today and cost something later.
- A design choice that sets a precedent other code will copy.
- A discrepancy with a spec, a standard, or a reference implementation: follow it, or deliberately
  diverge?
- Something the user asked for that contradicts the project's own rules or a decision already recorded.

**Skip it** when the choice is yours to make: naming, test structure, which of two equivalent idioms,
anything reversible in five minutes. Over-using this skill turns it into a ceremony tax and trains the
user to skim — which means the write-up that really mattered gets skimmed too.

Also skip it when there is only one real option. Presenting one option plus padding is not a decision
request, it is asking for permission you already have.

## Before you write a word: do the research

A fork you have not investigated is not a decision request, it is laziness with headings. Work through
this first, and do not stop at the first finding — the first finding is usually the symptom.

1. **Can you dissolve the fork?** Many apparent decisions have a discoverable right answer. If a spec,
   a standard or an upstream implementation settles it, read it and quote it. A dissolved question is
   worth more than a well-presented one.
2. **Is it already decided?** Check wherever the project keeps decisions — architecture decision records
   (`docs/adr/`, `DECISIONS.md`), design docs, issue tracker, commit history. If it is settled, you are
   reporting a decision, not opening one: link it and move on. Reopen only with genuinely new evidence,
   and say what that evidence is.
3. **Which options are even admissible?** Read the project's rules (`CLAUDE.md`, `AGENTS.md`,
   `CONTRIBUTING.md`, lint and CI configuration). A project that forbids a layer, a dependency or a
   category of debt has already ruled some options out. Present those as *excluded, with the reason*, or
   not at all — never as live choices.
4. **What is coming next?** Find the roadmap, the plan, the milestone, the sprint board. This feeds the
   forward-looking check below, and it changes the answer more often than anything else on this list.
5. **Re-validate.** Read your own findings back. Does the tension you are about to describe actually
   exist, or did you stop one level too early?

## The shape of the write-up

Four parts, always this order, because it is the order the user needs them in: what is wrong → what
could be done → what it costs → what you would do.

### Part 1 — the problem

```
## The problem

**What's happening** — <the observable fact, with evidence: file:line, a test name, a log line>

**Why it matters** — <the concrete consequence of leaving it; who or what breaks, and when>

**Why there's no obvious answer** — <the fork itself: the two good things that cannot both be had>
```

That third line is what makes the rest readable. Every real decision is two goods in tension — speed
against correctness, compatibility against cleanliness, today's bug against next month's refactor. Name
the tension explicitly and the options stop looking arbitrary.

**Plain language does not mean shallow.** Do not remove the detail; remove the jargon wrapped around
it. The user is an engineer and will follow any mechanism you explain — they simply do not have today's
context loaded.

**Expand every abbreviation the first time it appears in the conversation**, in a short parenthesis:
`TTL` (time to live — how long a cached entry stays valid), `N+1` (one query for the list, then one
more per row), `ADR` (architecture decision record). It costs you four words. The alternative is a
decision made on a guess about what a word meant. After the first expansion, use it bare.

This applies to project-local shorthand too — ticket prefixes, internal component names, milestone
codes. Those are the ones most likely to be skipped, because they feel like plain words to whoever has
been living in them.

### Part 2 — the options

```
## Options

### A — <short name>  ·  🩹 Dirty quick fix
<one sentence: what you would actually do>

- **Touches:** <files / systems>  ·  **Size:** <minutes | an afternoon | a few days>  ·  **Risk:** <low | medium | high>
- ✅ <pro — a concrete benefit>
- ❌ <con — a concrete cost, not a vibe>
- 🔭 <forward-looking note — only when there is one; see below>
```

**Tag the category in the heading, before any detail.** The tag tells the user how much to care before
they read a word, which is exactly what someone with less context needs first:

| Tag | What it means | What you must therefore say out loud |
| --- | --- | --- |
| 🩹 **Dirty quick fix** | Works now, leaves something behind for someone to pay later | Name the debt, and name **when** it comes due |
| 🔧 **Contained fix** | Correct, and the blast radius stays inside one area | — |
| 🏗️ **Structural change** | Several systems, real refactoring, days not hours | What stops working mid-flight, and whether it can land in pieces |
| 🧭 **Change the requirement** | Do not solve it — decide it away (drop it, accept the behaviour, redefine it) | Exactly what the user gives up |
| ⏸️ **Defer** | Leave it deliberately, with a trigger for revisiting | The trigger. Without one it is not a defer, it is forgetting |

Rules that keep the options honest:

- **Two to four.** Fewer than two is not a decision. More than four usually means you have not finished
  thinking — cluster the near-duplicates.
- **Every option must be one you would actually be willing to implement.** A strawman is not generosity,
  it is a rigged vote. If you would refuse to build it, leave it out, or list it as excluded with the
  reason.
- **Cons are costs, not adjectives.** "Less clean" says nothing. "The rounding rule then exists in two
  places and they will drift" is a con the user can weigh.
- **Include the do-nothing option whenever it is genuinely live** — it often is, and it is the one you
  are most likely to forget, because you have been staring at the problem.

### Part 3 — think ahead

This is not garnish. It changes the answer more often than the pros and cons do, and the user cannot
perform this check themselves, because it needs the roadmap *and* the code in one head.

For each option, ask: once the next planned step lands, is this work **deleted**, **untouched**, or
**load-bearing**?

- **Deleted** → say so **inside the option**, not in a footnote at the bottom. "Worth knowing up front:
  the migration next month replaces this module, so this fix gets thrown away with it." An option that
  dies soon can still win — it is cheap and its debt expires by itself — but that has to be weighed, not
  discovered afterwards.
- **Load-bearing** → the opposite warning. "The next milestone builds directly on this, so a shortcut
  here gets *harder* to remove later, not easier."
- **Untouched** → say nothing. Silence is the default; a forward-looking note on every option devalues
  the ones that matter.

The check runs the other way round too: if an option only becomes cheap *after* a step that is already
planned, that is an argument for deferring it, and it is often the strongest argument on the page.

### Part 4 — the recommendation

```
## My recommendation: B

<2–5 sentences: why this one, argued in terms of the tension you named in the problem>

**What would change my mind:** <the concrete fact or preference that flips it to A>
```

- **Pick one.** You have the most context in the room; withholding a view hands the cost of your
  knowledge back to the user. "It depends" is not neutrality, it is an unfinished sentence.
- **Say when it is close.** "B by a nose — if you would rather not touch that subsystem this week, A is
  defensible" is honest and genuinely useful.
- **If you recommend the quick fix, argue for it against the project's own stance.** Some projects
  forbid technical debt outright and require the sound alternative to be proposed first. Recommending a
  patch anyway is sometimes right, but it has to be argued rather than slipped through — and it has to
  name when the debt gets paid. "Later" is not a date.
- **If the user's own instruction created the fork** — it contradicts a spec, a project rule, or a
  settled decision — say so plainly here. This is the moment for it, not a hint earlier on.

Then **stop and wait.** Do not start implementing your recommendation in the same breath. A
recommendation that arrives with the code already written was never a question.

## Length — scale it to the stakes

| Stakes | Shape | Rough budget |
| --- | --- | --- |
| A local fork (which of two helpers to extend) | Problem in three sentences, two options, two bullets each, one-line recommendation | ~20 lines |
| A real design choice inside one system | The full structure, two or three options | ~50–70 lines |
| Architectural — outlives the feature, crosses a boundary, or is hard to reverse | Full structure, forward-looking notes, consequences worked through | As long as it needs, with no padding |

The real test is not length: **can the user decide without asking you a follow-up question?** If they
would have to ask "but what happens to X?", the answer to X belonged in the write-up. If they can
already decide, stop writing.

## After the user chooses

They have decided *what*. You still owe them *how*, before touching anything.

1. **Ask whatever is still open.** Keep asking until you could implement it without guessing. A guess
   made here is a bug the user pays for later, and they have no way to see it coming.
2. **Write a change plan.** What changes, where, in what order — and explicitly including
   **documentation**: the docs this invalidates, and the decision itself recorded wherever the project
   keeps decisions, *with the reasoning intact*, because the reasoning is what stops the question being
   relitigated in three months. Name the tests or checks that will prove it worked.
3. **Check you can actually carry it out.** If a step is one you cannot perform or cannot verify, say so
   in the plan rather than discovering it half-way through.
4. **Present the plan and ask whether to implement it.** Choosing an option was not a blanket yes to a
   plan they have not read yet.

## What ruins one of these

- **A fork you have not researched.** The user can tell, and it costs them their own time to do your
  reading.
- **Fake options.** Two real choices and one obvious loser is a worse write-up than two real choices.
- **Burying the recommendation** in hedges, or hiding it in the middle of the pros and cons.
- **Unexplained jargon.** Every unexpanded abbreviation is a small bet that the user will guess right.
- **Symmetry theatre** — three pros and three cons for every option, padded to match. If an option has
  one con and it is fatal, that is one con, in bold.
- **Deciding for them by omission.** Leaving out the option you dislike and then recommending the
  survivor is the exact failure this skill exists to prevent, wearing its uniform.
- **A wall of text.** If the user has to re-read a paragraph to find the decision, the write-up failed
  no matter how correct it was.

## A worked example

`references/worked-example.md` is a full-size decision request for a realistic problem — two services
that round money differently, so a report does not balance. Read it when you want to see the shape at
full scale, particularly how a forward-looking note flips the recommendation, and how a "we will
deliberately not do the textbook-correct thing" recommendation gets argued rather than assumed.
