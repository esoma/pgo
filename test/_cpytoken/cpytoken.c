// python
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include "tokenizer.h"

struct ModuleState
{
    PyTypeObject *tokenizer;
};

struct CpyTokenizer
{
    PyObject_HEAD
    PyObject *weakreflist;
    
    struct tok_state *tokenizer;
    int done;
};

static void
cpy_tokenizer_dealloc(struct CpyTokenizer *self)
{
    if (self->weakreflist)
    {
        PyObject_ClearWeakRefs((PyObject *)self);
    }
    
    if (self->tokenizer)
    {
        PyTokenizer_Free(self->tokenizer);
        self->tokenizer = 0;
    }
    
    PyTypeObject *type = Py_TYPE(self);
    type->tp_free(self);
    Py_DECREF(type);
}

static struct CpyTokenizer *
cpy_tokenizer_iter(struct CpyTokenizer *self)
{
    Py_INCREF(self);
    return self;
}

static PyObject *
cpy_tokenizer_iternext(struct CpyTokenizer *self)
{
    if (self->done)
    {
        PyErr_SetString(PyExc_StopIteration, "");
        return 0;
    }
    
    struct tok_state *tokenizer = self->tokenizer;
    
    char *start;
    char *end;
    int type = PyTokenizer_Get(tokenizer, &start, &end);

    PyObject *bvalue = PyBytes_FromStringAndSize(start, end - start);
    if (!bvalue){ return 0; }
    PyObject *value = PyUnicode_FromEncodedObject(
        bvalue,
        tokenizer->enc,
        0
    );
    Py_CLEAR(bvalue);
    if (!value){ return 0; }

    PyObject *token = Py_BuildValue("iO", type, value);
    Py_DECREF(value);
    if (!token){ return 0;}

    if (type == ENDMARKER || type == ERRORTOKEN)
    {
        self->done = 1;
    }
    
    return token;
}

static PyObject *tokenize(PyObject *self, PyObject *args);

static PyMemberDef tokenizer_type_members[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(struct CpyTokenizer, weakreflist), READONLY},
    {0}
};

static PyType_Slot tokenizer_spec_slots[] = {
    {Py_tp_dealloc, (destructor)cpy_tokenizer_dealloc},
    {Py_tp_iter, (getiterfunc)cpy_tokenizer_iter},
    {Py_tp_iternext, (iternextfunc)cpy_tokenizer_iternext},
    {Py_tp_members, tokenizer_type_members},
    {0, 0},
};

static PyType_Spec tokenizer_spec = {
    "_woosh_cpytoken.Tokenizer",
    sizeof(struct CpyTokenizer),
    0,
    Py_TPFLAGS_DEFAULT,
    tokenizer_spec_slots
};

static PyMethodDef methods[] = {
    {"tokenize",  tokenize, METH_VARARGS, 0},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module_def = {
    PyModuleDef_HEAD_INIT,
    "_woosh_cpytoken",
    0,
    sizeof(struct ModuleState),
    methods,
    0,
    0,
    0
};

PyMODINIT_FUNC
PyInit__pgo_cpytoken()
{
    PyObject *module = PyModule_Create(&module_def);
    if (!module){ goto error; }
    
    if (PyState_AddModule(module, &module_def) == -1){ goto error; }
    
    struct ModuleState *state = PyModule_GetState(module);
    assert(state);
    
#if PY_VERSION_HEX >= 0x03090000
    PyTypeObject *tok_type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &tokenizer_spec,
        0
    );
#else
    PyTypeObject* tok_type = (PyTypeObject *)PyType_FromSpec(&tokenizer_spec);
#endif
    if (!tok_type){ goto error; }
    state->tokenizer = tok_type;

    return module;
error:
    Py_CLEAR(module);
    return 0;
}

static PyObject *tokenize(PyObject *self, PyObject *args)
{
    PyObject *source_bytes;
    if (!PyArg_ParseTuple(
        args, "S",
        &source_bytes
    )){ return 0; };
    
    PyObject *module = PyState_FindModule(&module_def);
    struct ModuleState *module_state = PyModule_GetState(module);
    assert(module_state);
    
    struct CpyTokenizer *tokenizer = (struct CpyTokenizer *)PyType_GenericAlloc(
        module_state->tokenizer,
        0
    );
    if (!tokenizer){ return 0; }
    
    tokenizer->tokenizer = PyTokenizer_FromString(
        PyBytes_AS_STRING(source_bytes),
        1
    );
    if (!tokenizer->tokenizer)
    {
        Py_DECREF(tokenizer);
        return 0;
    }

    return (PyObject *)tokenizer;
}
