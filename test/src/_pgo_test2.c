
// python
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static struct PyModuleDef module_def = {
    PyModuleDef_HEAD_INIT,
    "_pgo_test2",
    0,
    0,
    0,
    0,
    0,
    0
};

PyMODINIT_FUNC
PyInit__pgo_test2()
{
    return PyModule_Create(&module_def);
}
