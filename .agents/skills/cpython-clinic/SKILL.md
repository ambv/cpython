---
name: cpython-clinic
description: Convert and maintain Argument Clinic blocks in CPython C code (input syntax, regen, MethodDef checks).
---

# Argument Clinic

Clinic (`Tools/clinic/clinic.py`, `make clinic`) generates argument-parsing
boilerplate for C builtins. Source: `Tools/clinic/clinic.py`; full reference
in the devguide (clinic tutorial + how-tos). Clinic is CPython-internal —
never use it for external extensions.

## Block anatomy

```c
/*[clinic input]
module._Class.method
    arg: converter = default
        Per-parameter docstring, indented further.
    /
    *
Summary line, one 80-column line, then body.
[clinic start generated code]*/
... generated output, never hand-edited ...
/*[clinic end generated code: output=... input=...]*/
```

- Input lives between `/*[clinic input]` and `[clinic start generated code]*/`;
  output between there and the checksum line. Checksums detect drift and
  regenerate — editing output is always lost, so change the input instead.
- First block in a file declares `module`/`class` (C pointer type + `PyTypeObject*`).
- `/` marks preceding params positional-only; `*` starts keyword-only.
  Drop the old C-quoted docstring signature line — `help()` builds it now.
- Converters: legacy `'O'`, `'i'` etc. mirror `PyArg_Parse*` format units
  (list via `clinic.py --converters`); prefer real converters (`object`,
  `int`, `str(encoding=...)`, `bool`, `Py_buffer`, ...). `*`/`/` markers and
  defaults infer the calling convention — a literal `|` is unnecessary.
- Directives: `as name` (rename C basename), `-> int` (return converters,
  `-1` signals error), `@text_signature`, `@critical_section[ obj...]`
  (free-threading), `@getter`/`@setter`/`@deleter`, `defining_class`,
  `[from 3.N]` deprecation markers, `destination`/`output` presets for
  relocating output (check generated `clinic/*.h` files in!).

## Converting a PyArg_Parse* function

1. Skip functions using `O&`, `O!`, `es`, `et` variants, multiple
   `PyArg_ParseTuple` calls, or non-`PyArg_Parse*` parsing — convert those
   only with the advanced-converter how-tos.
2. Write the input block (dotted Python path, params, summary docstring).
3. Regenerate, `#include "clinic/<file>.c.h"`, delete the old prototype,
   arg-parsing code, and arg declarations; keep the opening `{`.
4. Verify sameness before/after: identical parse function
   (`PyArg_ParseTuple` vs `AndKeywords`), identical format string up to
   `:`/`;`, identical second args (length vars, encodings, converters),
   identical `PyMethodDef` (replace the static entry with the generated
   `..._METHODDEF` macro, no trailing comma).
5. New `_Py_ID(...)` in output: run `make regen-global-objects`.
6. Rebuild, run the relevant tests, confirm no new warnings — and that
   `inspect.signature` now works on the function.
