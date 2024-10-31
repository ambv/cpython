#ifndef Py_INTERNAL_ASYNCIO_H
#define Py_INTERNAL_ASYNCIO_H

#ifdef __cplusplus
extern "C" {
#endif

#ifndef Py_BUILD_CORE
#  error "this header requires Py_BUILD_CORE define"
#endif

// External introspection helpers.
struct root_fut_per_loop {
    PyObject *loop;  // strong ref
    PyObject *root;  // FutureObj* or TaskObj*; strong ref
    struct root_fut_per_loop *next;
};

#ifdef __cplusplus
}
#endif
#endif /* !Py_INTERNAL_ASYNCIO_H */
