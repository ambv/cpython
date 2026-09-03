---
name: cpython-pr
description: Take a CPython change from branch to merged PR (titles, NEWS, patchcheck, review loop, CI, backports).
---

# CPython Pull Request Flow

## Branch and patch

- Branch from `upstream/main`, never commit to `main`:
  `git checkout -b fix-issue-12345 upstream/main`.
- One issue per commit; no unrelated cosmetics. Titles are imperative with
  no trailing period. PR titles start with the issue: `gh-12345: ...`
  (`gh-` links are preferred over `#NNNNN`).
- Open an issue first for nontrivial changes; only trivial ones (typos,
  comment/section rephrases) may use the `skip issue` label instead.
- Before pushing: `make patchcheck` (docs? tests? NEWS entry? configure
  regenerated?) and the full test suite green.
- NEWS entries via `blurb add` into `Misc/NEWS.d/next/<Area>/`
  (`<date>.gh-issue-<N>.<nonce>.rst`, user-visible wording, 80 columns,
  no leading marker). Skippable only for docs, tests, strictly internal
  changes, or duplicates. User-facing changes also need `Doc/whatsnew/`.
- Push to the fork (`git push origin <branch>`) and open the PR against
  `python/cpython:main`. New features target `main` first, always —
  including bug fixes (backports come later).
- Inspect tracker state with read-only `gh` commands (`gh issue view`,
  `gh pr view`, `gh pr diff`); pushes, merges, labels, and comments always
  require explicit human instruction first.

## CLA and CI

- Every commit-author email must have signed the CLA; check with
  `git config user.email` (squash merges re-verify the primary email,
  which bites backports using a different address).
- Keep CI green: compare failures with the Release Status buildbot
  dashboard — failures already there predate the change.
- `Update branch` merges base into the PR: use only with good reason
  (it notifies watchers and burns CI). Re-run jobs only with core/triage
  rights; otherwise push an empty commit or ask, and file an issue for flakes.
- `test-with-buildbots` / `test-with-refleak-buildbots` labels and
  `!buildbot <regex>` comments need a triager or core member to trigger —
  ask for help rather than working around it.

## Review loop

- Address review in new pushed commits. Never amend, squash, or force-push:
  reviewers diff commit-to-commit to verify their comments were addressed,
  and squash-merge discards the intermediates anyway.
- When reporting test results, include platform and version.
  Praise-worthy parts deserve comments too, not just problems.
- If a reviewer pushed to the branch, `git pull origin <branch>` before
  editing. No review after a month: ping the issue, then Discourse
  (Core Development).
- After merge, delete the branch locally and on the fork.
- Maintain `.agents/worklog/pr-<N>.md` throughout (learnings, state,
  decisions); it is how the next session — human or agent — resumes.

## Backports

- `needs backport to X.Y` labels trigger miss-islington; on conflicts use
  `cherry_picker <merged-sha> <branch>` (find the squash hash via
  `git rev-parse ":/gh-<PR>"`), resolve, test, `git add`, then
  `cherry_picker --continue`.
- Keep the original message; drop the old `(#XXXXX)` number; append
  `(cherry picked from commit <sha>)`. Title: `[3.x] gh-YYYYY: ... (GH-ZZZZZ)`.
- Maintenance branches fail CI on ABI changes without an updated
  `Doc/data/pythonX.Y.abi` — loop in the release manager.
