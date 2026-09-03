---
name: cpython-review
description: Review someone else's CPython PR the way the project asks (reproduce first, platform/version reporting, CI triage).
---

# Reviewing CPython Pull Requests

Reviewing is a first-class contribution — the tracker bottleneck is
review time, not patches. A partial review (reproduce + play with the code
+ comment) beats none.

## Reproduce-first checklist

1. Build the checkout and run the test suite baseline.
2. Reproduce the issue in the `./python` REPL from the linked steps.
3. Check out the PR: `git fetch upstream pull/N/head:pr_N && git switch pr_N`
   (or `gh pr checkout N`, which also configures push-back
   when the author allowed maintainer edits).
4. Rebuild if any C file changed; confirm the issue is fixed; probe corner
   cases and related issues the author may have missed.
5. Run the affected modules' tests; run the entire suite before calling
   anything merge-ready.

## What to write

- Report test results with system and version (e.g. Ubuntu 24.04, macOS 15,
  Windows 11) — "tested, works" without that is nearly useless.
- Comment on what is good, not just bad; when requesting changes, suggest how.
- Paste the traceback into the comment when pointing at CI failures; thousands
  of lines of logs are not a pointer.
- Verify the PR checklist a triager would: right base branch, style guides
  (PEP 7/8), proper tests, docs changes, NEWS entry, no conflicts, CI green.
- Never dismiss another core developer's review, and never reassign priority
  or close as a drive-by: triagers close only after consulting a core dev,
  and closed-issue disagreements go to Discourse, not to reopen wars.

## Triaging CI failures on the PR

1. Compare against the Release Status buildbot dashboard — a failure present
   there predates the PR; find the introducing PR and say so.
2. Match flags and `--randseed` from the failing stdio link to reproduce
   locally (see cpython-test for the bisection procedure).
3. `Update branch` only to check whether base fixed it, not reflexively.
4. Flaky-looking failure with no matching issue on the tracker: file one
   before re-running, so the flake is tracked.
