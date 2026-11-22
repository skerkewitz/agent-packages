# sker-project

Skills for how a project is run: conventions a project opts into, with the scripts that keep
them honest. Install this package into the projects that follow them, not globally. The skills
for how the agent works with you in any project are in [`sker-power`](../sker-power).

| Skill | Use it when |
|---|---|
| `sker-adr` | The project keeps architecture decision records with IDs made from the time and a hash of the title (`ADR-6FCBBNSH`), so that records written on parallel branches never collide. Writes, supersedes and cites records, sets the scheme up in a new project and moves numbered records to it. Comes with `new_adr.py` (makes ID, file and table row) and `check_adr.py` (checks table, files and citations), which setup copies into the project. |

## Install

```bash
apm install skerkewitz/agent-packages/packages/sker-project#sker-project/v1.0.0   # into a project
```
