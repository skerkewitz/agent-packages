# agent-packages

My AI agent primitives (skills, prompts, instructions, agents, hooks), split into several
independent [APM](https://microsoft.github.io/apm/) packages grouped by topic.

Each folder under `packages/` is one package and can be installed on its own.
The repo root is **not** a package (no `apm.yml` here).

## Packages

| Package | Description |
|---|---|
| [`sker-power`](packages/sker-power) | Workflow skills: brainstorm a change, hand decisions back with costed options, implement a brainstorm decision |

## Install

```bash
# into the current project, pinned to a release
apm install skerkewitz/agent-packages/packages/sker-power#sker-power/v1.0.0

# user-level (all projects on this machine)
apm install -g skerkewitz/agent-packages/packages/sker-power
```

## Layout

```
packages/<name>/
├── apm.yml
├── README.md
└── .apm/
    ├── skills/<skill>/SKILL.md   (+ reference files, scripts)
    ├── instructions/*.instructions.md
    ├── prompts/*.prompt.md
    ├── agents/*.agent.md
    └── hooks/*.json
```

## Versioning

Per-package tags: `<name>/vX.Y.Z` (e.g. `gosu/v1.2.0`). Bump `version` in the
package's `apm.yml` before tagging.

## Development

```bash
cd packages/<name> && apm compile --validate
```

Generated output (`.claude/`, `.agents/`, `apm_modules/`, `AGENTS.md`, …) is git-ignored and
must never be committed.
