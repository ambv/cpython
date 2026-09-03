---
name: cpython-test
description: Run CPython's test suite the way reviewers expect (regrtest flags, refleaks, ordering bisection, test layout).
---

# CPython Tests

Always run tests with the freshly built in-tree interpreter (`./python`,
`./python.exe` on macOS) — never the system Python.

## Running

- Full suite: `./python -m test -j0`.
- One file, verbose: `./python -m test -v test_abc`.
- One case: `./python -m unittest -v test.test_abc.TestClass`.
- Touched C code: add refleak checking, `./python -m test test_x -R :`
  (`-R warmups:repeats`, e.g. `-R 3:2`, for control).
- Strenuous (pre-PR): `./python -bb -E -Wd -m test -r -w -uall`
  (`-r` random order, `-w` re-runs failures, `-uall` enables all resources).
- Direct execution (`./python Lib/test/test_x.py`) is a local-debug aid only;
  some modules do not support it at all.
- Never pytest: the suite is unittest-based. Filter with `--match GLOB`,
  never `-k`.
- Pure-Python `Lib/` edits need no rebuild — rerun tests directly.
  Rebuild only for C changes (and rerun the affected tests right after).

## Interpreting results

- "Unexpected skips" usually mean an optional module failed to build —
  compare with the configure/build summary, not the test.
- Whole suite must pass, not just the seemingly-affected tests; interference
  between modules is real and reviewers will reject partial runs.
- No warnings are allowed under strenuous flags; fix or file an issue.

## Ordering-dependent failures

1. Copy the exact flags, resources, and `Using random seed:` value from the
   failing buildbot's stdio link.
2. Reproduce with `--randseed <seed>` added to the same command.
3. Bisect by writing the printed test sequence to a file and running
   `--fromfile` on shrinking halves — almost always a two-test interference.
4. Never use `-j` while diagnosing: parallel workers isolate tests in pristine
   subprocesses and hide the interference.

## Writing tests

- Location and naming: `Lib/test`, `test_` prefix; test packages need
  `load_tests()` in `__init__.py`. C API tests go in `Modules/_testcapi/`
  (new file per feature, registered in `parts.h` + build files); internal C
  API tests go in `Modules/_testinternalcapi.c`.
- Rely on `test.support`; study the file's existing tests first for the
  portability precautions (locales, resources, cleanup) reviewers expect.
- Cover normal behavior and error conditions; match the file's whitebox or
  blackbox style; every test method must assert.
- Coverage work: trace-based collection,
  `./python -m test -j0 --coverage test_x --coveragedir DIR`;
  measure per-module (`--source=`), ignore import-time global statements
  for startup-imported modules, and file an issue plus PR when done.
- Never alter or bypass existing tests, or remove desired functionality,
  to make a failure pass — that is not a fix and will get the PR closed.
