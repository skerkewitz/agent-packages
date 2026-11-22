---
name: sker-pr
description: Every change to a repository goes through a pull request, from branch to release. Start a change on its own branch and worktree made from the integration branch, open its pull request with what changed, how it was verified and what follows from it, answer review comments on GitHub, merge after the user's approval and clean up; and make a release (version pull request, pull request into the release branch, tag). The project's own rules (branches, verify commands, worktree setup, release steps, reviewer) come from a "## Pull requests" section in its CLAUDE.md. Use it for every change to a repository that works this way, when the user asks to implement or fix something, to open or update a pull request, to look at feedback on a PR, to merge one, to make a release, or invokes /sker-pr.
---

# sker-pr: every change through a pull request

Every change gets its own branch and worktree, made from the latest integration branch, and
reaches it only through a pull request. The user reviews and approves on GitHub; Claude merges
after the approval and cleans up. The main checkout stays on the integration branch, so a
session working there sees that branch either without a change or with all of it, never half of
one. Several sessions can then work at once, each in its own worktree.

## The project's rules

Read the "## Pull requests" section of the project's CLAUDE.md (or AGENTS.md) before the first
step. It says what differs from the defaults below, and it wins over them:

| Setting | Default |
|---|---|
| Integration branch (`BASE`) | `develop` if `origin/develop` exists, else the repository's default branch |
| Release branch (`RELEASE`) | `main` when `BASE` is `develop`; none otherwise, and a release is only a tag |
| Worktree folder | `<name of the main checkout>-wt/<branch>`, next to the main checkout |
| Worktree setup | nothing; the section may name commands to run after creating a worktree and before removing one |
| Reviewer (`USER`) | the user's GitHub account, from their instructions; ask if it is not there |
| Verify | none known: ask the user once, and suggest adding the command to the section |
| What follows | the documents changed and compatibility; the section adds the project's own topics |
| Never public | the list in "Everything sent to GitHub is public"; the section adds the project's own |
| Release | ask the user for the version; the section names the preparation steps and the tag format (default `v<version>`) |

A project without the section works with the defaults. If one of them does not fit, ask, and
offer to write the answer into the section. A sketch of a section:

```markdown
## Pull requests

The steps are the `sker-pr` skill. For this project:

- Branches: changes go into `develop`; a release goes from `develop` into `main`, tagged `v<version>`.
- Worktrees: in `myproject-wt/<branch>`. After creating one, `ln -s MAIN/.cache WT/.cache`;
  before removing it, `rm -f WT/.cache`.
- Verify: `./gradlew build`. Changes to the output also run the benchmark, with numbers before and after.
- What follows: the generated code (size), the style guide, the book pages that go stale.
- Never public: the customer's data.
- Release preparation: version by the rule in docs/roadmap.md, raised in build.gradle.kts.
```

Paths and names used below:

- `MAIN`: the main checkout, the folder that holds the repository's `.git`. From any worktree:
  `dirname "$(git rev-parse --path-format=absolute --git-common-dir)"`. It stays on `BASE`.
  Never edit, build, commit or switch branches in it. The one exception is the fast-forward
  after a merge (see `merge`).
- `WT`: the worktree of a change, `<worktree folder>/<branch>`.
- `REPO`: `owner/name` of the repository on GitHub (`gh repo view --json nameWithOwner`).
- `WRAP`: the wrapper the user's or the project's instructions name for acting on GitHub, such
  as `gh-as-bot`; empty if they name none.

## Working through the wrapper

If the instructions name a wrapper, every `gh` command, every `git push` and every git command
that writes a commit or a tag (`commit`, a `merge` that is not a fast-forward, `rebase`, `tag`)
runs through it: `WRAP gh pr create ...`, `WRAP git push ...`. A plain `gh` or `git push` would
act as someone else: never use one, and if the wrapper fails, stop and tell the user. The
commands below all carry `WRAP`.

Give texts as files, never through standard input: a commit message with `git commit -F
<file>`, a description or comment with `--body-file <file>`. A wrapper may read standard input
itself, and a file can be checked for leaks before it is sent. Write the files to the session's
scratchpad, never into the repository.

Claude never approves a pull request; that is the user's. Claude merges only after the user's
approval (see `merge`).

## Everything sent to GitHub is public

Treat every pull request, comment, commit message and committed file as public: a private
repository can be opened or forked later. GitHub keeps the edit history of descriptions and
comments, and a merge commit keeps the commits of its branch, so neither an edit nor a later
commit takes text back. Before every `git push`, `gh pr create`, `gh pr edit`, `gh pr comment`
and `gh api ... -f body=`, check what goes out (the new commits' diff and messages, and the
text) for:

- paths on the user's machine: home folders, WSL mounts (`/mnt/<drive>/`), Windows drives and
  user folders, the session's scratchpad, `/tmp/claude-*`. Name a place by its path in the
  repository (`tools/`, `docs/testing.md`) or say where it is ("next to the main checkout").
  Paths already in the repository may be quoted as they are;
- user names, host names, email addresses (the author line of a commit is the exception), and
  anything else about the user's machine or accounts;
- passwords, tokens and keys (`github_pat_`, `ghp_`, `gho_`, private key blocks, cloud keys),
  and files that hold them (`.env`, `*.pem`, credential files, `.claude/settings.local.json`);
- anything from Claude's memory or the conversation that the repository does not already
  contain. Some of the user's plans are private on purpose; when unsure, leave it out or ask;
- what the project's section lists as never public.

The mechanical part of the check, for the lines a branch adds and for a text before it is sent:

```
LEAK='/home/|/Users/|/mnt/[a-z]/|[A-Za-z]:\\|/tmp/claude|github_pat_|gh[opsu]_[A-Za-z0-9]{20}|PRIVATE KEY|AKIA[0-9A-Z]{16}|password *[:=]'
git -C WT diff origin/BASE... | grep '^+' | grep -nE "$LEAK"
git -C WT log --format=%B origin/BASE.. | grep -nE "$LEAK"
grep -nE "$LEAK" <text file>
```

Look at every hit; a hit can be harmless (this skill's own pattern, a path that is in the
repository already). The pattern does not find the rest of the list above: read the text for
it. If something has already gone out, stop and tell the user what and where. Removing it
takes a force-push or the deletion of a revision on GitHub, and that is the user's decision.

## Invocation

- `/sker-pr start <branch>`: create the branch and its worktree.
- `/sker-pr open`: verify the branch and open its pull request into `BASE`.
- `/sker-pr feedback <N>`: read the review of pull request N and answer it.
- `/sker-pr merge <N>`: merge pull request N after the user's approval, then clean up.
- `/sker-pr release`: make a release.
- `/sker-pr status`: list the open pull requests, the worktrees and the branches, and say what
  each waits for.

When the user asks for a change without naming a step, start with `start` and go on to `open`
when the work is done. Long unattended runs follow the same steps; the run is the work between
`start` and `open`.

## start

1. Branch name: short, lower case, words joined by `-`, saying what the change is (`ci`,
   `inline-once-called`, `release-0.7.5`). Check that neither a local nor a remote branch of
   that name exists.
2. Create it from the latest `BASE`, without upstream tracking (with tracking, a plain
   `git push` would go to `BASE`), run the project's worktree setup, and push the branch:

   ```
   git -C MAIN fetch origin
   git -C MAIN worktree add --no-track -b <branch> WT origin/BASE
   WRAP git -C WT push -u origin <branch>
   ```

3. Do all work in `WT`: edits, builds, tests, benchmarks, commits. Commit each step that is done
   and verified (`WRAP git -C WT commit -F <file>`), and push it. Follow the project's CLAUDE.md
   as everywhere.

If the work turns out to be a different change than the branch name says, tell the user; don't
fold a second change into the branch.

## open

1. Bring the branch up to date with `BASE`. As long as nobody has reviewed it, rebase:
   `git -C WT fetch origin && WRAP git -C WT rebase origin/BASE`, then
   `WRAP git -C WT push --force-with-lease`. Once a pull request is open, merge instead
   (`WRAP git -C WT merge origin/BASE`) and never force-push.
2. Verify in `WT` with the project's verify commands, plus what the change needs on top: the
   numbers before and after for anything that claims to be faster or smaller. Note what you ran
   and what came out; the description reports it.
3. Write the description to a file in the scratchpad, following the template below and the
   `sker-natural-writing` skill where it is installed. It is written for the user reviewing on
   GitHub, who has not watched the work.
4. Check the branch and the description for leaks (see "Everything sent to GitHub is public").
5. Open it:

   ```
   WRAP gh pr create -R REPO --base BASE --head <branch> --reviewer USER --title "<title>" --body-file <file>
   ```

   The title is a short sentence in the style of the commit log. The user is asked for a review
   on every pull request. Give the user the link.
6. If the repository has CI, it builds the pull request's last commit. Wait for it and check
   that it passed: `WRAP gh pr checks <N> -R REPO --watch` (run it in the background; a build
   takes minutes). If the build failed, `WRAP gh run view <id> -R REPO --log-failed` shows why
   (the id is in the link `gh pr checks` prints). Fix it as a change to the open pull request.

### Template

```markdown
## What

What the change does, in a few sentences. The reason for it, if the title does not say it.

## How

How it is done, as much as a reviewer needs to read the diff: the approach, the files that
matter, anything surprising. Decisions with a record are cited by its ID.

## Verified

What was run and what came out: the build (number of tests), benchmarks with numbers before
and after, a manual check and what it showed. Say what was not checked and why.

## What follows

What the change means beyond its diff: the project's own topics from its section, the
documents changed, compatibility. Leave out the lines that do not apply.

## Open

What is left to do or decide, and what the reviewer should look at closely. Leave the section
out if there is nothing.
```

End it with the attribution line the session's instructions ask for, if any. Scale it to the
change. A one-line fix gets a sentence under What and one under Verified; a week of
optimisation gets tables.

## Changes to an open pull request

Every push to a pull request that is already open gets a comment, so the user can follow what
changed since they last looked. This holds whatever caused the change: a review comment, the
user's word in the session, something Claude found itself, a merge of `BASE`, a resolved
conflict. After the push, one comment per push:

```
🤖 <short title of the fix>

Problem: what was wrong or missing, and how it came up (review comment, own check, failed build).
Fix: what was changed and why this way.
Commits: <hash> <subject>, ...
Verified: what was run again and what came out.
```

Post it with `WRAP gh pr comment <N> -R REPO --body-file <file>`, after the leak check. A merge
of `BASE` without conflicts needs only a line ("Merged develop at <hash>; build passed"). If
the fix changes what the description says, update the description too (`WRAP gh pr edit`), and
say so in the comment.

## feedback

1. Read everything on the pull request:

   ```
   WRAP gh pr view <N> -R REPO --comments
   WRAP gh api repos/REPO/pulls/<N>/reviews
   WRAP gh api repos/REPO/pulls/<N>/comments
   ```

   The last call gives the comments on lines of the diff, with `id`, `path`, `line` and
   `in_reply_to_id`.
2. Claude's own comments start with `🤖`; with a wrapper that acts as an app, they also appear
   under the app's name with `[bot]` after it. A comment from the user's account without `🤖`
   is the user's.
3. For each point: if it asks for a change, make it in `WT` as a new commit, verify as in
   `open`, push. If it asks a question, answer it. If you disagree, say so with the reason and
   leave the decision to the user. Answer a comment on a line in its thread:

   ```
   WRAP gh api repos/REPO/pulls/<N>/comments/<id>/replies -F body=@<file>
   ```

   and after the push write the comment of "Changes to an open pull request", one section per
   point of the review.
4. If the description no longer fits (new numbers, a changed approach), update it with
   `WRAP gh pr edit <N> -R REPO --body-file <file>`.

## merge

1. Check the approval: an approving review by `USER` on GitHub, or the user's word in the
   session. `WRAP gh pr view <N> -R REPO --json reviews,commits` shows the reviews and when the
   commits came. If commits were pushed after the approving review, the approval needs the
   user's word that it still holds, or a new review. Claude never approves. Without an
   approval, stop.
2. Check that it can be merged: `WRAP gh pr view <N> -R REPO --json mergeStateStatus` must say
   `CLEAN`, and if the repository has CI, `WRAP gh pr checks <N> -R REPO` must show the build
   passed. If `BASE` has moved and the branch conflicts, merge `origin/BASE` into the branch in
   `WT` (`WRAP git -C WT merge origin/BASE`), resolve, verify, push, and tell the user what the
   resolution did before merging.
3. Merge with a merge commit, and keep the branch for now (`--delete-branch` would try to
   switch the checkout it runs in). Squash and rebase merges drop the single steps of a branch,
   each of them verified, and make `BASE` and `RELEASE` diverge.

   ```
   WRAP gh pr merge <N> -R REPO --merge
   ```

4. Fast-forward the main checkout, but only if it has no changes to tracked files (another
   session may be working there); otherwise tell the user it is behind:

   ```
   git -C MAIN fetch origin
   [ -z "$(git -C MAIN status --porcelain --untracked-files=no)" ] && git -C MAIN merge --ff-only origin/BASE
   ```

5. Clean up: the project's steps before removing a worktree, then the worktree and the branch.
   `git worktree remove` refuses a worktree with changes; if it does, stop and ask.

   ```
   git -C MAIN worktree remove WT
   git -C MAIN branch -d <branch>
   WRAP git -C MAIN push origin --delete <branch>
   ```

## release

The user decides when to release. With a release branch it is two pull requests and a tag;
without one, the tag alone.

1. Version. Propose the next one by the project's rule, or ask. The user confirms it.
2. Preparation, as a normal change: `start release-<version>`, then in `WT` the project's
   release preparation (raise the version where the project keeps it, bring generated
   documents in step), and its verify commands. `open` it with the title "Version <version>".
   Under What, list the pull requests merged since the last tag:
   `git log --first-parent --oneline <last tag>..origin/BASE`, or all of `BASE`'s history if
   there is no tag yet. Merge it as usual after the approval.
3. With a release branch, open the release pull request from `BASE` itself:

   ```
   WRAP gh pr create -R REPO --base RELEASE --head BASE --reviewer USER --title "Release <version>" --body-file <file>
   ```

   The description lists the pull requests in the release, one line each, and what the
   project's users notice. After the approval: `WRAP gh pr merge <N> -R REPO --merge`. Never
   pass `--delete-branch` here: `BASE` stays.
4. Tag the merge commit (on `RELEASE`, or on `BASE` without a release branch) and push the tag:

   ```
   git -C MAIN fetch origin
   WRAP git -C MAIN tag -a <tag> origin/RELEASE -m "<project> <version>"
   WRAP git -C MAIN push origin <tag>
   ```

## status

```
WRAP gh pr list -R REPO --state open
git -C MAIN worktree list
git -C MAIN branch -a --no-merged origin/BASE
```

For each open pull request say whether it waits for the user (review), for Claude (feedback
to answer, a failed CI build, conflicts with `BASE`) or is approved and ready to merge. Name
worktrees whose branch is merged or gone; remove them only if they are in the worktree folder
and clean, and ask about the others, which may belong to another session.
