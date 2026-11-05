# sker-power

Skills for thinking a change through with the user, carrying it out without overreach, and documenting Java/Gosu code.

| Skill | Use it when |
|---|---|
| `sker-brainstorm` | You want to think a topic, bug or feature idea through as a dialog. Changes no files; writes a summary to `docs/brainstorm/<topic>_<date>.md` at the end. |
| `sker-explain-and-solve-problem` | The agent hits a fork it should not settle alone. It explains the problem, lays out costed options and recommends one. |
| `sker-implement-idea` | You want a brainstorm summary's Decision built: only that, with the new behaviour proven, documentation, specs and requirements updated, and the project's full verification run. |
| `sker-javadoc` | You want Java or Gosu source documented with concise, evidence-based Javadoc, including private members and instance fields. |

The three workflow skills work together: `sker-brainstorm` → summary → `sker-implement-idea`, which
hands forks back through `sker-explain-and-solve-problem`.

## Install

```bash
apm install skerkewitz/agent-packages/packages/sker-power#sker-power/v1.0.0   # into a project
apm install -g skerkewitz/agent-packages/packages/sker-power               # user-level
```
