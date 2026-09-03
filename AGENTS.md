# AI agent guidance

CPython has a [policy on the use of AI tools](https://devguide.python.org/getting-started/ai-tools/).
All use of AI tools and agents when working on or interacting with CPython
must follow it.

> [!important]
> **Primary directive**: Read the policy before making or proposing any changes.
> Key rules are inlined below so they apply even when the page is not fetched;
> the link remains the full reference.

When acting on this repository, apply the policy's core principles:

- Consider whether the change is necessary.
- Make minimal, focused changes.
- Follow existing coding style and patterns.
- Write tests that exercise the change.
- Keep backwards compatibility with prior releases in mind.

## Repository layout

- `Lib/`: pure-Python standard library. `Modules/`: C extensions —
  accelerators stay underscore-private (e.g. `_csv` backs `csv`).
- `Objects/`, `Python/`: builtins, types, runtime, eval loop.
  `Include/`: C headers. `Parser/`, `Grammar/`: tokenizer and PEG grammar.
- `Lib/test/` mirrors sources: `Lib/zipfile/` → `Lib/test/test_zipfile*`,
  `Modules/_csv.c` → `Lib/test/test_csv.py`. Test packages need `load_tests()`.
- `Doc/`: end-user docs (`.rst`). `InternalDocs/`: maintainer docs.
  `Tools/`: build tooling including Argument Clinic. `Misc/NEWS.d/next/`: news.
- Never edit `**/clinic/**` outputs or other generated files; regenerate instead.

## Build from source

Unix/macOS (Windows uses `PCbuild/build.bat -c Debug` for a Debug build):

- Always develop under a pydebug build, even for pure-Python changes:
  `./configure --config-cache --with-pydebug && make -j$(getconf _NPROCESSORS_ONLN)`.
- Run the interpreter in place (`./python`, `./python.exe` on macOS);
  never install it, and avoid `--enable-shared` in a work directory.
- Missing optional modules or "unexpected skips" in tests almost always mean
  missing system headers: `apt-get build-dep python3`, `dnf builddep python3`,
  or `brew bundle --file=Misc/Brewfile`, then re-run `configure` and `make`.
- Generated files are checked in: after editing `configure.ac` run
  `make regen-configure` (needs Docker/Podman for the pinned autoconf);
  after touching C builtins run `make clinic` (never hand-edit Clinic output,
  change the input block instead); `make regen-all` when unsure what to refresh.
- New `_Py_ID` identifiers require `make regen-global-objects`.
- Limited C API additions need a `Misc/stable_abi.toml` entry plus
  `make regen-limited-abi` and `make check-limited-abi`.
- Vendored third-party dependency updates must also update `Misc/sbom.spdx.json`
  via `make regen-sbom`.
- New compiler warnings fail CI (`Tools/build/check_warnings.py`): refactor to
  avoid them, or document why and update the sorted `Tools/build/.warningignore_*`
  counts. Fewer warnings than expected must decrement the counts too.

## Tests

- Full suite: `./python -m test -j0`. Single file: `./python -m test -v test_abc`.
  Single case: `./python -m unittest -v test.test_abc.TestClass`.
- C changes: check reference leaks (`./python -m test test_x -R :`).
  Strenuous mode: `./python -bb -E -Wd -m test -r -w -uall`.
- Tests live in `Lib/test` (`test_` prefix; test packages need `load_tests()`).
  Rely on `test.support`, and study the file's existing tests first — they encode
  the portability precautions reviewers expect.
- Ordering-dependent failure? Reproduce the buildbot's exact flags and
  `--randseed` from its stdio link, bisect with `--fromfile`, and never use
  `-j` while diagnosing (it isolates tests in pristine subprocesses).
- PRs are not accepted without proper tests, and the whole suite must pass —
  running only the seemingly-affected tests is not sufficient.
- Never alter or bypass existing tests, or remove desired functionality,
  to make a failing test pass.

## Patches and style

- One issue per commit; no unrelated cosmetic changes. Commit titles are
  imperative with no trailing period (`gh-12345: ...`).
- Python code follows PEP 8, C code follows PEP 7.
  Install the lint hook: `pre-commit install --allow-missing-config`.
- No type annotations in `Lib/` (the stdlib stays annotation-free);
  no trailing whitespace; preserve final newlines.
- C API tiers are internal (`Include/internal/`, leading `_`), unstable
  (`PyUnstable_`), public, and limited. New public API must follow reference
  counting rules (never steal or return borrowed references, strong returns
  only; `NULL`/`-1` plus a raised exception on error) and should be cleared
  with the C API working group first.
- New C accelerator modules require a working, tested pure-Python
  implementation (PEP 399); exported symbols must start with `Py` or `_Py`
  (`make smelly` verifies).
- Backwards compatibility (PEP 387): new arguments stay optional with
  behavior-preserving defaults; deprecations last at least two releases.
- NEWS entries via `blurb add` (`Misc/NEWS.d/next/<Area>/<date>.gh-issue-<N>.<nonce>.rst`),
  required for anything user-visible; user-facing changes also need a
  `Doc/whatsnew/` entry reusing the NEWS wording.
- Docs are reStructuredText (3-space indent, 80 columns): use semantic roles
  (`:func:`, `:meth:`, `:class:`, `:mod:`, `:gh:`, `:source:`), mark new APIs
  with `versionadded:: next`, build with `cd Doc && make venv && make html`
  (or `SOURCES="..."` for single pages), lint with `make check`.
  Typo fixes stay small and need no issue; never add author bylines.

## GitHub pull request flow

- Branch from `upstream/main` (never commit to `main`); `origin` is the fork,
  `upstream` is `python/cpython`. Title PRs `gh-NNNNN: ...` (`gh-` links are
  preferred over `#NNNNN`).
- Open an issue first for nontrivial changes; only trivial ones may use the
  `skip issue` label. Run `make patchcheck` before pushing.
- Every commit-author email must have signed the CLA (`git config user.email`
  shows yours; squash merges re-check the primary email on backports).
- Keep CI green: compare failures against the Release Status buildbot dashboard
  before assuming they are yours; use `Update branch` only with good reason;
  re-run jobs only with core/triage rights (otherwise push an empty commit or
  ask); file an issue for flakes.
- Address review in new pushed commits — never amend or force-push; reviewers
  diff commit-to-commit. Report what you tested, including platform/version.
- If a reviewer pushed to the branch, pull before editing. No review after a
  month: ping the issue, then ask on Discourse (Core Development).
- After merge, delete the branch. Backports: `needs backport to X.Y` labels
  trigger miss-islington; on conflicts use `cherry_picker`, keep the original
  message, and append `(cherry picked from commit <sha>)`.
- Find reviewers in `devguide`'s experts index and `.github/CODEOWNERS`
  (auto-requested); @mention platform maintainers for platform-specific issues.

## Reviewing other people's pull requests

- Reproduce the issue in the `./python` REPL first, then check out the PR
  (`git fetch upstream pull/N/head:pr_N`), rebuild for C changes, and probe
  corner cases the author may have missed.
- Call a PR merge-ready only with the full suite passing. Comment on what is
  good as well as bad, suggest how to fix requested changes, and paste the
  traceback (not just its existence) when pointing at CI failures.

## Security: hard rules

- Never file a public issue for a suspected vulnerability — report privately
  via a GitHub Security Advisory ticket.
- Verify every LLM-found vulnerability report before submitting (no hallucinated
  APIs); keep reports to a few sentences plus a proof-of-concept script that
  exits nonzero when vulnerable. No severity scores, no PDFs or binaries.
- Not vulnerabilities: documented behavior (`pickle`, `eval`, `ctypes`),
  sandbox escapes, attacker-controlled launch conditions, unhandled exceptions
  alone, dependency bugs Python merely redistributes, or issues on unsupported
  platforms or experimental features.

## Working notes

- Keep an engineering notebook so state survives across sessions, one file
  per task under `.agents/worklog/`: `pr-<N>.md` for PR work,
  `branch-<name>.md` (slashes become dashes) otherwise. Record learnings,
  decisions, and status; update it after commits. This convention is
  tool-neutral — do not use vendor-specific directories for project state.
- Scratch exploration and prototypes go in `.agents/sandbox/`, never the repo
  root or source tree. Worklogs and sandbox content are never committed.

## Finding work and getting help

- Good first tasks carry the `easy` label; check `Linked PRs` and comment with
  an ETA before starting so work is not duplicated.
- Ask in Discourse (Core Development for process, Ideas for language proposals,
  Core Workflow for bots/infra), `#python-dev` on Libera.Chat, or via the core
  mentorship program. Never silent-close or re-scope: stay on the assigned issue,
  and do not freelance language changes (proposals need discussion first, never
  pre-formatted as a PEP, and most are rejected).
