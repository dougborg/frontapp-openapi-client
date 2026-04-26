---
name: review-pr
description: >-
  Address PR review comments — fetch all unresolved comments, fix the issues,
  validate with `uv run poe check`, commit, push, and reply to each comment
  on GitHub. Use when asked to handle PR review feedback.
argument-hint: "[PR number]"
allowed-tools:
  - Bash(gh api *)
  - Bash(gh pr *)
  - Bash(git status)
  - Bash(git diff *)
  - Bash(git log *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(git push *)
  - Bash(git rebase *)
  - Bash(git stash *)
  - Bash(git fetch *)
  - Bash(git merge *)
  - Bash(uv run poe check)
  - Bash(uv run poe agent-check)
  - Bash(uv run poe fix)
---

# PR Review Comment Workflow

Address all unresolved PR review comments: fix the code, validate, commit, push, and
reply.

## Phase 1: Identify the PR + check its state

Fetch everything needed in **one** call:

```bash
gh pr view ${ARGUMENTS:-} --json \
  number,url,title,headRefName,baseRefName,mergeable,mergeStateStatus,statusCheckRollup
gh repo view --json nameWithOwner --jq '.nameWithOwner'
```

If `$ARGUMENTS` is empty, `gh pr view` auto-detects from the current branch.
If no PR is found, tell the user and stop.

Store:

- `headRefName` — the PR's branch. **You must be on this branch** before any commits.
  If `git rev-parse --abbrev-ref HEAD` doesn't match, run
  `git checkout <headRefName>` (stash dirty work first if needed).
- `baseRefName` — use `origin/<baseRefName>` as the rebase/log target throughout.
  Do **not** assume `main`.

### Detect stacked PRs early

If `<baseRefName>` is **not** the repo's default branch (e.g. it's another feature
branch like `chore/harness-phase-a`), this PR is **stacked** on another PR.
That changes how rebases and force-pushes propagate — see the "Stacked PR" call-out
in Phase 5.

### If `mergeable: CONFLICTING`

1. `git fetch origin <baseRefName>`
2. `git merge origin/<baseRefName>`
3. Resolve each conflicted file by reading both sides; keep our branch's intent
   integrated with the base's changes.
4. `git add <resolved files>` then continue the merge.

### If `mergeStateStatus` is not `CLEAN` / `HAS_HOOKS`

`statusCheckRollup` already lists every check (no need for a second `gh pr checks`
call). Triage by failure type:

- **Code issue** (lint / type-check / test) → fix as part of Phase 4.
- **Flaky CI** (timeout, transient network) → note in the summary, don't block.
- **Repo-config issue** (Dependency Graph disabled, missing secret, deprecated
  action) → note in the summary, link the GitHub-org-or-repo settings page that
  needs the change, and don't block on it. These aren't fixable from a PR.

**Resolve conflicts before addressing review comments** — comments may no longer
apply after the resolution.

## Phase 2: Fetch all review comments

Fetch every review comment on the PR:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate
```

Also fetch review threads to check resolved status:

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        reviewThreads(first: 100) {
          nodes {
            isResolved
            comments(first: 100) {
              nodes {
                id
                databaseId
                body
                path
                line
                author { login }
              }
            }
          }
        }
      }
    }
  }
' -F owner="{owner}" -F repo="{repo}" -F number={number}
```

Present a summary table of all comments:

| #   | Status     | File:Line     | Author   | Comment (truncated)   |
| --- | ---------- | ------------- | -------- | --------------------- |
| 1   | unresolved | src/foo.py:42 | reviewer | "Consider using..."   |
| 2   | resolved   | src/bar.py:10 | reviewer | "Typo in variable..." |

Skip resolved threads — only work on **unresolved** comments.

## Phase 3: Triage each unresolved comment

For each unresolved comment:

1. **Read the affected file** and surrounding context
1. **Check if already fixed** — the code may have changed since the comment was posted
1. **Classify** the comment:
   - **fix needed** — code change required
   - **already fixed** — issue was addressed in a prior commit, just needs a reply
   - **acknowledge** — valid point but deferring, or explaining why current approach is
     correct
   - **disagree** — the comment is wrong (e.g. an automated reviewer hallucinated a
     missing import, or claims a file doesn't exist when it does). Verify with
     `ls` / `grep` / a small smoke test, then reply with the citation that proves
     the comment wrong. Don't silently dismiss.

If a comment has prior replies, check whether the replies actually resolved the concern.
If not, treat it as still needing action.

**Automated reviewers (Copilot, etc.) produce false positives often enough that
"disagree" is a routine outcome — not an exception.** Don't bend the code to satisfy a
hallucinated finding.

## Phase 4: Fix all issues

Make all necessary code changes across affected files. Remember this repo's constraints:

- NEVER edit generated files (`api/**/*.py`, `models/**/*.py`, `client.py`)
- Use `unwrap_unset()`, `unwrap_as()`, `is_success()` helpers per CLAUDE.md patterns
- Resilience is at the transport layer — don't wrap API methods with retries

Then validate:

```bash
uv run poe check
```

This runs format + lint + type-check + tests. **ALL must pass.** If validation fails:

1. Run `uv run poe fix` for auto-fixable lint/format issues
1. Fix remaining issues manually
1. Re-run `uv run poe check` until clean

## Phase 5: Commit, rebase, and push

The goal is a **clean commit history** — review fixes should be folded into the commits
they logically belong to, not piled on as separate "fix review comments" commits. Don't
squash everything into one commit; preserve meaningful commit boundaries.

### Step 1: Stage and commit fixes

Stage only the files that were changed (never use `git add -A` or `git add .`):

```bash
git add <file1> <file2> ...
```

Create a temporary fixup commit:

```bash
git commit -m "$(cat <<'EOF'
fixup! <original commit subject line this fix belongs to>

- Description of fix 1
- Description of fix 2

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

If fixes span multiple original commits, create multiple fixup commits — one per target
commit.

If fixes don't clearly map to an existing commit (e.g., they address a cross-cutting
concern), create a standalone commit with a descriptive message instead.

### Step 2: Rebase to fold fixups into their target commits

```bash
git fetch origin <baseRefName>
git rebase --autosquash origin/<baseRefName>
```

This automatically reorders and squashes `fixup!` commits into their targets. After the
rebase, verify with:

```bash
git log origin/<baseRefName>..HEAD --oneline
```

The result should be a clean set of logical commits — no "fix review comments" or
"address feedback" commits.

### Step 3: Force-push the rebased branch

Since the branch is already pushed, a force-push is required after rebasing:

```bash
git push --force-with-lease
```

Use `--force-with-lease` (not `--force`) to avoid overwriting changes pushed by others.

**NEVER reply to comments before pushing.** Replies confirm the fix is live.

### Stacked PRs (this PR's base is another feature branch)

If Phase 1 detected `<baseRefName>` is **not** the default branch (e.g. it's
`chore/harness-phase-a` for a PR that stacks on PR #18), force-pushing this branch
is fine — but force-pushing the **parent** in a separate `/review-pr` run rewrites
this branch's base, breaking the chain. Two scenarios:

**This PR is the parent in a stack** (other PRs target this branch as their base):

After your `git push --force-with-lease`, every child PR's branch needs to be rebased
onto the new SHA:

```bash
# For each child PR's local branch:
git checkout <child-branch>
git rebase --onto <parent-branch> <OLD_PARENT_SHA> <child-branch>
git push --force-with-lease
```

`<OLD_PARENT_SHA>` is the SHA the child was previously based on (find with
`git log <child-branch>~N --oneline | grep <parent-subject>`). The plain
`git rebase <parent-branch>` re-applies the parent's old commits and conflicts —
use `--onto` to skip them.

**This PR is a child** (its base is some other feature branch the user is also
reviewing in another `/review-pr` session):

If the parent has been rewritten upstream, your `git rebase --autosquash
origin/<baseRefName>` from Step 2 will re-apply the parent's old commits and conflict.
Detect this by `git fetch origin <baseRefName>` first; if `origin/<baseRefName>`
moved, use `git rebase --onto origin/<baseRefName> <OLD_BASE_SHA>` instead of plain
`--autosquash`.

**About to merge the parent?** `gh pr merge --delete-branch` on the parent
deletes its branch on origin, which auto-closes every child PR whose `baseRefName`
points at that branch. The auto-closed PRs cannot be reopened (GitHub refuses
because the base ref is gone) — you'd have to open fresh PRs from the same head
branch with content rebased onto a still-existing base.

Before merging a parent in a stack, **flip every child's base to the eventual
destination (usually `main`)**:

```bash
gh pr edit <child-pr-number> --base main
```

This is a metadata-only change (no force-push). The child PR will then show its
diff against `main` until the parent merges; once the parent merges, you can
rebase the child's branch onto fresh `main` to drop the parent's now-redundant
commits. Doing this *before* the parent merge means no PRs auto-close.

## Phase 6: Reply to each comment

After pushing, reply to every unresolved comment. Pipe through
`jq -r '.html_url'` so the response is a tidy one-line confirmation, not the
~3 KB JSON blob `gh api` dumps by default:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments/{comment_id}/replies \
  -X POST -f body='...' | jq -r '.html_url'
```

Reply format by classification:

- **Code fix**: "Fixed in `<short-sha>` — [describe what was changed]. [mention
  tests if added]"
- **Already fixed**: "Already addressed in `<short-sha>` — [brief explanation]"
- **Acknowledged/deferred**: "Acknowledged — [reason for deferring]. Tracked in
  #NNN." (must include a GitHub issue link)
- **Disagree**: "Disagree — [evidence]. [What you checked, e.g. `ls path/`,
  `grep -n …`, `docs/api-facts.yaml: tags.X.endpoints[…]`, smoke-test result.]
  Marking as not-applicable; happy to revisit if there's a repro." Don't be
  hostile — be specific.

  When the comment makes a factual claim about the generated API surface
  (module name, response shape, helper presence), `docs/api-facts.yaml` is
  the authoritative cite — it's CI-validated, so a single grep against that
  file refutes most automated-reviewer hallucinations. Example: a reviewer
  claiming `api/tags/list_tags.py` doesn't exist is refuted by
  `summary.list_endpoints_with_field_results: tags.list_tags`.

Reply to **EVERY** unresolved comment. None should be left without a response.

Cite the **rewritten** SHA from Step 3, not the original commit, since
`--autosquash` produced a new SHA.

## Phase 7: Update PR description (only if scope changed)

**Skip this phase entirely** if the review fixes are minor (typos, doc tweaks,
clarifications) and the existing description is still accurate. Overwriting a
rich PR body with a stub template is destructive.

Update only when scope materially changed (new files added, behavior changed,
test plan no longer applies). Fetch the existing body first and amend it:

```bash
gh pr view {number} --json body --jq .body > /tmp/pr-body.md
# Edit /tmp/pr-body.md in place to reflect current scope
gh pr edit {number} --body-file /tmp/pr-body.md
```

Review the commit log (`git log origin/<baseRefName>..HEAD --oneline`) before
deciding whether scope changed.

## Phase 8: Summary

Print a final summary for the user:

- Number of comments addressed (fixed / already fixed / acknowledged)
- Files changed
- Validation result (tests, lint, type-check)
- Any comments that couldn't be addressed, with explanation

## Important Rules

- **Fix first, reply after push** — never reply before the code is pushed
- **Reply to every comment** — even if just acknowledging
- **No shortcuts** — `uv run poe check` must pass; never use `--no-verify`, `noqa`, or
  `type: ignore`
- **Be specific in replies** — describe what changed, don't just say "done"
- **Clean history via rebase** — fold review fixes into the commits they belong to using
  `fixup!` + `--autosquash`; don't pile on "fix review comments" commits, but also don't
  squash everything into one commit — preserve meaningful commit boundaries
- **Evaluate existing replies** — if a comment already has replies, check whether the
  issue was actually resolved; if not, fix it and add a new reply
- **No ignores or suppressions** — never use `noqa`, `type: ignore`, or skip tests to
  make validation pass
- **File issues for deferred work** — if a review comment identifies a valid issue that
  is out of scope or too large to fix in this PR, create a GitHub issue with
  `gh issue create` before replying. The reply MUST include the issue number. Never
  defer work without a tracking issue.
