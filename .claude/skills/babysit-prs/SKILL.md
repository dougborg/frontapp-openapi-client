---
name: babysit-prs
description: >-
  Watch CI on multiple open PRs in parallel, surface real failures with their
  job-log tails, and chain into `/review-pr` when comments arrive. Use when 2+
  PRs are open at once and individually polling each would burn context.
argument-hint: "[pr-numbers...] (default: all open PRs authored by current user)"
allowed-tools:
  - Bash(gh pr *)
  - Bash(gh api *)
  - Bash(gh run *)
  - Bash(gh auth status)
---

# Babysit Open PRs

Watch CI on every PR in scope until each one is either green-and-mergeable or has a
real (non-flaky) failure that needs human attention.

## PURPOSE

When several PRs are open simultaneously (the harness work that landed in PRs
#19/#20/#21/#23, the four-PR sweep on 2026-04-26, etc.) the agent otherwise wastes
context polling each one's checks individually. This skill consolidates the watch
loop into one event stream: one punchy line per state change, log tails only on
real failures, automatic handoff to `/review-pr` when comments arrive.

## CRITICAL

- **Don't reinvent watching.** Use `gh pr checks <N> --watch --interval 15` per PR;
  it already streams check transitions over a long-poll connection. Aggressive
  `sleep N; gh pr checks` chains burn context and rate-limit budget.
- **Don't trigger on the first red.** A single transient failure (network blip,
  flaky integration test) should not page the human. Re-poll once before alerting
  — see "Flaky vs. real failure" below.
- **Don't fix anything from this skill.** This is a watch-and-report loop. When a
  PR has real CI failures or new review comments, **invoke `/review-pr <N>`**
  rather than fixing inline.
- **Stop when scope is empty.** A PR that gets merged, closed, or marked
  `mergeable: CONFLICTING` while we watch leaves the watch set; if the set
  becomes empty, exit cleanly and summarize.

## ASSUMES

- `gh auth status` is authenticated (skill will check up front).
- The user is OK with watching for as long as it takes — typical CI on this repo
  is ~5-8 min per PR, and this skill runs until every watched PR settles.

## STANDARD PATH

### Phase 1: Discover the watch set

If `$ARGUMENTS` lists explicit PR numbers, use them. Otherwise default to every
open PR authored by the current user:

```bash
gh pr list --state open --author '@me' \
  --json number,title,headRefName,baseRefName,mergeable,mergeStateStatus
```

For each PR, also fetch the initial check rollup so we know the starting state
(don't alert on a failure that was already there before we started watching —
note it as "pre-existing" in the summary):

```bash
gh pr view <N> --json number,statusCheckRollup,reviews,mergeable

# Cache initial review-comment + issue-comment counts to compare against later.
# `--paginate` matters: without it, `length` plateaus at the page size (30) and
# new comments past that boundary will be missed. Aggregate per-page lengths:
review_comment_count=$(gh api --paginate \
  repos/{owner}/{repo}/pulls/<N>/comments \
  --jq 'length' | awk '{sum+=$1} END {print sum+0}')
issue_comment_count=$(gh api --paginate \
  repos/{owner}/{repo}/issues/<N>/comments \
  --jq 'length' | awk '{sum+=$1} END {print sum+0}')
```

Print the watch set as a table. If empty, stop and tell the user.

| PR  | Title                     | Base | Status     | Reviews / comments |
| --- | ------------------------- | ---- | ---------- | ------------------ |
| 35  | feat(client): drafts      | main | PENDING    | 0 / 0              |
| 36  | refactor(mcp): summary    | main | SUCCESS    | 1 / 2              |

### Phase 2: Launch the watch loop

For each PR in the watch set, **start `gh pr checks --watch` as a background
job** so the streams run in parallel rather than serially:

```bash
gh pr checks <N> --watch --interval 15 --fail-fast
```

Use `Bash` with `run_in_background: true`, one call per PR. The harness will
deliver each line of output as a notification — let `Monitor` surface them
rather than polling `BashOutput` in a tight loop.

In parallel, every ~60s poll for new review activity (`gh pr checks --watch`
won't catch comments). Watch **both** review-thread comments and the PR
discussion (issue-level) comments, since either kind can carry a request that
needs `/review-pr` follow-up:

```bash
# Same `--paginate` + sum dance as Phase 1 — `length` on the first page alone
# stops growing past 30 items.
gh api --paginate repos/{owner}/{repo}/pulls/<N>/comments \
  --jq 'length' | awk '{sum+=$1} END {print sum+0}'
gh api --paginate repos/{owner}/{repo}/issues/<N>/comments \
  --jq 'length' | awk '{sum+=$1} END {print sum+0}'
gh pr view <N> --json reviews --jq '.reviews | length'
```

Cache the previous counts; emit a `new-comment` event when any of the three
goes up.

### Phase 3: Triage each event

Per PR, classify what just changed:

- **All checks green + no new comments** → emit `PR #N all green, ready to
  merge` and **remove from watch set**.
- **One check failed, others still pending** → wait. Don't alert yet; the
  remaining checks may pass or also fail (a real bug usually trips multiple
  checks). Note the failing check name internally.
- **All checks complete, ≥1 failed** → fetch the failure log tail and triage
  flaky vs. real (next section).
- **New review comments arrived** → emit `PR #N has N new comment(s) — invoke
  /review-pr <N>` and **remove from watch set** (the loop's job is done; the
  human or `/review-pr` takes over).
- **PR closed / merged / went CONFLICTING** → emit one-liner and remove from
  watch set.

Each event is **one line**, prefixed with `PR #N`. Keep it skim-friendly.

### Phase 4: Flaky vs. real failure

When a PR has finished CI with ≥1 red check:

1. Fetch the failure log tail:

   ```bash
   gh run view <run-id> --log-failed | tail -60
   ```

2. Apply the heuristic:

   - **Flaky if** the tail contains a network error (`ECONNRESET`,
     `dial tcp`, `503 Service Unavailable`), a timeout from a known-flaky
     integration test, or a transient action error like
     `The runner has received a shutdown signal`. **Action:** re-trigger the
     job once via `gh run rerun <run-id> --failed`, log
     `PR #N <job> flaky-retry triggered`, and **keep watching**.
   - **Real otherwise** (assertion error, type-check error, lint diff,
     compile failure). **Action:** emit
     `PR #N <job-name> failed: <one-liner from log tail>` and **remove from
     watch set**. The human or a follow-up `/review-pr` invocation handles
     the fix.

3. **Cap retries at one per job.** A second flaky-looking failure after
   re-trigger is treated as real — back-to-back transient failures on the
   same job are rare enough that human eyes are warranted.

### Phase 5: Termination + summary

The loop terminates when the watch set is empty. Print a final summary:

| PR  | Outcome                              | Next action                       |
| --- | ------------------------------------ | --------------------------------- |
| 35  | All green                            | Ready to merge                    |
| 36  | New comments                         | `/review-pr 36`                   |
| 37  | Real failure: `pytest tests/foo`     | Investigate locally               |
| 38  | Closed by user mid-watch             | None                              |

If a PR ended in "real failure" or "new comments", surface that PR number in the
final line so the user can copy-paste into `/review-pr`.

## EDGE CASES

- **A PR is freshly pushed and CI hasn't started yet.** `statusCheckRollup` is
  empty for ~30s. Treat empty rollup as PENDING; don't classify it as green.

- **`gh pr checks --watch` exits with a non-zero code on first red** because
  of `--fail-fast`. That's expected — fold it into the triage path; don't
  treat the exit code as a tool error.

- **A PR's base is another feature branch (stacked PR).** Watch it the same
  way, but in the summary flag it as `stacked on <base>` so the human knows
  the merge order matters. Do NOT auto-rebase; that's the user's call.

- **Rate limits.** Each `gh pr checks --watch` holds one long-poll connection;
  watching ~10 PRs in parallel is fine. The 60s comment-polling loop adds
  ~1 req/min/PR, also fine. If `gh` returns `API rate limit exceeded`, back
  off the comment poll to 5min and continue.

- **The user's `gh` CLI is not authenticated.** `gh auth status` fails — stop
  immediately and tell the user.

- **A PR was created by Dependabot / renovate (not the user).** The default
  scope (`--author '@me'`) excludes them. If the user wants those watched too,
  they need to pass the PR numbers explicitly.

## After

When the loop ends with PRs in "new comments" or "real failure" state, the
natural follow-up is `/review-pr <N>` for each. Surface those PR numbers in
the final summary so the user can chain without re-discovering them.
