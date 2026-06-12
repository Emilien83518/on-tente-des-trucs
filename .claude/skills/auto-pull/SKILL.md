---
name: auto-pull
description: Always pull the latest version of the current branch from GitHub before starting any work. Trigger this skill at the very start of every conversation, before creating a branch, before coding anything, before running tests, or whenever the user says "pull", "sync", "update the branch", "make sure we're up to date", or "get the latest". This prevents working on outdated code.
---

# Auto Pull — Stay in Sync

Before touching any code, make sure the local branch matches what is on GitHub.

## Step 1 — Check the current branch

```bash
git branch --show-current
```

## Step 2 — Pull the latest from the remote

```bash
git pull origin $(git branch --show-current)
```

If there is nothing new, git will say `Already up to date.` — that is fine, just continue.

## Step 3 — Also sync main

Even if you are working on a feature branch, it is good to know if `main` has moved forward:

```bash
git fetch origin main
```

Then check if the current branch is behind main:

```bash
git log HEAD..origin/main --oneline
```

If there are commits in `main` that are not in the current branch, warn the user:
> "Warning: `main` has new commits that are not in this branch. You may want to merge or rebase before continuing."

## Step 4 — Report to the user

Tell the user clearly:
- Which branch you are on
- Whether the pull brought in any new changes (and list the files if so)
- Whether `main` has moved ahead

Then proceed with whatever the user asked for.

## Important rules

- Never skip this step even if you think the code is already up to date — always verify
- If the pull fails (e.g. merge conflict), stop and tell the user before doing anything else
- Never force-push or reset — only pull
