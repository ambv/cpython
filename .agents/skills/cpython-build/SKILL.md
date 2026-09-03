---
name: cpython-build
description: Configure, build, and regenerate a CPython checkout (pydebug builds, regen targets, Clinic, warnings).
---

# CPython Build

Work in a CPython checkout with a configured `origin` (fork) / `upstream`
(`python/cpython`) remote pair. Build before testing anything.

## Standard development build (Unix/macOS)

Always develop under a pydebug build, even for pure-Python changes:

```bash
./configure --config-cache --with-pydebug && make -j$(getconf _NPROCESSORS_ONLN)
```

- Run the interpreter in place: `./python` (`./python.exe` on macOS,
  which avoids clashing with the `Python/` directory). Never install it.
- Avoid `--enable-shared` in a work directory; use `--prefix=/tmp/python`
  if you fear an accidental install.
- Delete `config.cache` (and usually `make clean`) when switching compilers
  or the build environment otherwise changes significantly.
- Windows: `PCbuild/build.bat -c Debug`, then run `PCbuild/amd64/python_d.exe`.

## Missing modules

If the build summary lists modules "not found", or tests report unexpected
skips, install system headers and rebuild (`configure` + `make`):

- Debian/Ubuntu: enable `deb-src`, then `apt-get build-dep python3` plus `pkg-config`.
- Fedora/RHEL: `dnf install dnf-plugins-core && dnf builddep python3`.
- macOS: `xcode-select --install`, then `brew bundle --file=Misc/Brewfile`
  with the version-specific `GDBM_*`/OpenSSL flags from the devguide.

## Regeneration (generated files are committed)

- `configure.ac` edited: `make regen-configure` (uses Docker/Podman for the
  pinned GNU Autoconf; bare `autoreconf` is not equivalent). Commit
  `configure`, `pyconfig.h.in`, and `aclocal.m4` too.
- C builtins touched: `make clinic`, or `python3 Tools/clinic/clinic.py <file>`.
  Never hand-edit generated output — change the input block and regenerate
  (checksum mismatches are always resolved in favor of regeneration).
- Unsure what is stale: `make regen-all`.
- New `_Py_ID` identifiers: `make regen-global-objects`.
- Limited C API: add the declaration under `Include/` (not `cpython/` or
  `internal/`) guarded by `Py_LIMITED_API`, append to `Misc/stable_abi.toml`,
  then `make regen-limited-abi` and `make check-limited-abi`.
- Maintenance branches: regenerate `Doc/data/pythonX.Y.abi` in the same
  container image CI uses (`.github/workflows/regen-abidump.sh`); the CI
  artifact also carries the updated file after release-manager approval.
- Vendored dependency changed: edit `Misc/sbom.spdx.json` metadata, then
  `make regen-sbom`, and `git diff` the result before committing.
- New C accelerator module: wire `Modules/Setup.stdlib.in`,
  `configure.ac` (`SRCDIRS` + `PY_STDLIB_MOD*`), `Makefile.pre.in` deps,
  `PCbuild` project files, then `make regen-configure && make regen-all &&
  make regen-stdlib-module-names`.

## Compiler warnings

CI tracks warnings per file (`Tools/build/check_warnings.py`,
`Tools/build/.warningignore_*`, sorted). Refactor to avoid new warnings;
if one is unavoidable, document why in the PR and bump the count.
Fewer warnings than expected also fail — decrement or remove the entry.
