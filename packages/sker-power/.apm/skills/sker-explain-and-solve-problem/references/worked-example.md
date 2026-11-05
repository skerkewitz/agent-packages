# Worked example — a decision request at full size

An illustrative example, not a real project. The scenario is invented; the point is the **shape**, and
in particular three things that are easy to get wrong:

- the problem statement names the *tension*, not just the symptom;
- one option is excluded up front, with its reason, instead of being offered as a fake choice;
- the forward-looking check **flips the recommendation away from the textbook-correct answer**, and that
  is argued out loud rather than assumed.

Everything below the line is the message as it would be sent to the user.

---

## The problem

**What's happening** — Monthly revenue reports disagree with the invoices they are built from, by a few
cents per invoice. `InvoiceService` rounds each line to 2 decimal places and then adds the lines up
([InvoiceService.java:212](src/billing/InvoiceService.java#L212)). `ReportingService` adds the raw
values first and rounds once at the end
([ReportingService.java:88](src/reporting/ReportingService.java#L88)). On a 40-line invoice the two
answers can differ by up to 20 cents, and the nightly reconciliation job has been failing on roughly
1 invoice in 30 since the quarterly price change went in.

**Why it matters** — Finance reconciles reports against invoices by hand when the job fails, so this is
currently costing someone an afternoon a month. The invoice is the legally binding number, so the
report is the side that is wrong — but nothing in the code says so, which is why the two drifted apart
in the first place.

**Why there's no obvious answer** — Two good things are in tension. **One rounding rule in one place**
is obviously right and is what DRY (don't repeat yourself — one rule, one place) asks for. But
`ReportingService` is scheduled for replacement next quarter, so any structural work there is partly
building something we are about to delete. Cheap-and-temporary and correct-and-permanent genuinely
point in different directions here.

**Not an option:** changing the stored column from `DOUBLE` to `DECIMAL(12,2)`, which would remove the
class of problem entirely. The schema is frozen for the duration of the tenant migration
(ADR-014 — architecture decision record 14, in `docs/adr/`), and that freeze is not mine to lift.

## Options

### A — Widen the reconciliation tolerance · 🩹 Dirty quick fix
Accept a difference of up to 25 cents per invoice in the nightly job so it stops failing.

- **Touches:** one constant in `ReconciliationJob` · **Size:** minutes · **Risk:** low to ship, high to live with
- ✅ Stops the manual afternoon immediately, today, with no design work.
- ❌ It hides the *class* of error, not just this instance. The first time a real billing bug lands with
  an error under 25 cents, the one check that would have caught it stays green.
- ❌ **The debt comes due the day someone trusts the report.** That is not a date anyone controls, which
  is what makes this the worst kind of debt rather than the cheapest.

### B — Round per line in reporting too · 🔧 Contained fix
Make `ReportingService` round each line before summing, exactly as the invoice does.

- **Touches:** `ReportingService.calculateTotal` and its tests · **Size:** an afternoon · **Risk:** low
- ✅ Reports become correct — actually correct, not tolerated — and the reconciliation job goes back to
  meaning something.
- ✅ Small and reviewable; no other consumer changes.
- ❌ The rounding rule now exists in two places and must stay in step. That is precisely how we got
  here, so this fixes today's symptom and leaves the mechanism intact.
- 🔭 This code is deleted next quarter with the rest of `ReportingService`, so the duplication expires by
  itself. A short-lived duplicate is a much smaller sin than a permanent one.

### C — Extract a shared `Money` type · 🏗️ Structural change
One `Money` value type with the rounding rule inside it, used by billing, reporting and the export job.

- **Touches:** ~30 call sites across three packages, plus the export job's serialisation format ·
  **Size:** a few days · **Risk:** medium — money arithmetic touched everywhere at once
- ✅ The textbook answer, and permanently right: one rule, one place, impossible to drift.
- ✅ Pays off again for every future consumer of money arithmetic.
- ❌ Money arithmetic in three packages changes in one pull request; a mistake here is a billing
  mistake, and billing mistakes are the expensive kind.
- 🔭 **Worth knowing before you weigh this:** the new analytics pipeline will not compute money at all —
  it reads stored line totals. So roughly half of this work is being done for a consumer that will not
  exist next quarter. The billing half survives; the reporting half does not.

### D — Stop recomputing money in reporting · 🧭 Change the requirement
Reporting reads the stored line totals the invoice already wrote, instead of recalculating them from
quantity and unit price. There is then only one place where money is rounded, because there is only one
place where money is *computed*.

- **Touches:** `ReportingService.calculateTotal`, one repository query, the report fixtures ·
  **Size:** a day · **Risk:** low
- ✅ Removes the duplicated rule rather than synchronising it — the two numbers cannot disagree, because
  there is now only one number.
- ✅ Makes the "the invoice is the source of truth" rule explicit in the code, where it was previously
  only true by coincidence.
- ❌ Reporting can no longer show a breakdown for invoices written before line totals were stored
  (before 2024-03). Those would show a total with no per-line detail.
- ❌ Gives up the accidental cross-check we had: two independent computations agreeing was weak
  evidence that both were right.
- 🔭 This is what the new analytics pipeline is specified to do anyway. Doing it now is next quarter's
  design arriving early, not work that gets thrown away.

## My recommendation: D

The tension was cheap-and-temporary against correct-and-permanent, and D refuses the trade rather than
picking a side: it is roughly a day's work, it is permanently correct, and it is the same shape the
replacement service is already specified to have. C is the answer I would give in any other quarter —
but half of C is scaffolding for a component that is being deleted, and a shared `Money` type introduced
across three packages for a few cents of drift is a large blast radius for a small problem. B is
perfectly defensible and I would not argue hard against it; it is simply a day cheaper for a duplicate
rule I would rather not reintroduce, even a short-lived one.

I would not take A. It is the only option that leaves the system less able to detect the next billing
bug than it is today, and the project's stance on debt says the sound alternative gets proposed first —
this is that alternative, and it costs a day.

**What would change my mind:** if the analytics pipeline slips past next quarter or is cancelled, C
stops being scaffolding and becomes the right answer. And if the pre-2024-03 invoices *do* need per-line
detail in reports, D's first con is disqualifying rather than cosmetic — that is a question for Finance,
and I would rather ask them than assume.
