
# make sure setuptools is imported first to make it do all its hackery with
# distutils and cython
import setuptools

# cython
from Cython.Build import cythonize
# pytest
import pytest
# python
import os
import pathlib
import platform
import sys
import tempfile
from warnings import warn
# setuptools
from setuptools import find_packages, Extension


TEST_DIR = pathlib.Path(__file__).parent.absolute()
REL_TEST_DIR = TEST_DIR.relative_to(pathlib.Path.cwd())


@pytest.fixture
def extension():
    return Extension(
        '_pgo_test',
        sources=[str(TEST_DIR / 'src/_pgo_test.c')],
        language='c'
    )
    

@pytest.fixture
def extension2():
    return Extension(
        '_pgo_test2',
        sources=[str(TEST_DIR / 'src/_pgo_test2.c')],
        language='c'
    )
    
    
@pytest.fixture
def cython_extension():
    try:
        os.remove(str(TEST_DIR / 'src/_pgo_test_cython.c'))
    except FileNotFoundError:
        pass
    return cythonize(
        str(TEST_DIR / 'src/_pgo_test_cython.pyx'),
        language_level='3',
    )[0]
    
    
@pytest.fixture
def mypyc_extension():
    try:
        from mypyc.build import mypycify
    except ImportError:
        # mypy doesn't work on PyPy < 3.8:
        # https://github.com/python/typed_ast/issues/111
        if not (platform.python_implementation() == 'PyPy' and
            sys.version_info < (3, 8)):
            raise
        mypycify = None

    if mypycify is None:
        yield Extension(
            '_pgo_test_mypyc',
            sources=[str(TEST_DIR / 'src/_pgo_test_mypyc_not_installed.c')],
            language='c'
        )
    else:
        target_dir = tempfile.TemporaryDirectory()
        yield mypycify(
            [str(TEST_DIR / 'src/_pgo_test_mypyc.py')],
            target_dir=target_dir.name,
        )[0]
        target_dir.cleanup()
    
    
@pytest.fixture
def py_modules():
    return ['_pgo_test_module']
    
    
@pytest.fixture
def packages():
    return ['_pgo_test_package']
    
    
@pytest.fixture
def package_dir():
    return {"": str(REL_TEST_DIR / 'src')}
    
    
@pytest.fixture
def script_name():
    return TEST_DIR / 'setup.py'
    
    
@pytest.fixture
def argv():
    original_argv = sys.argv
    sys.argv = ['setup.py']
    yield sys.argv
    sys.argv = original_argv


@pytest.fixture
def pgo_lib_dir():
    dir = tempfile.TemporaryDirectory()
    yield dir.name
    try:
        dir.cleanup()
    except FileNotFoundError:
        pass
        
        
@pytest.fixture
def lib_dir():
    dir = tempfile.TemporaryDirectory()
    yield dir.name
    try:
        dir.cleanup()
    except FileNotFoundError:
        pass
    
    
@pytest.fixture
def pgo_temp_dir():
    dir = tempfile.TemporaryDirectory()
    yield dir.name
    try:
        dir.cleanup()
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_dir():
    dir = tempfile.TemporaryDirectory()
    yield dir.name
    try:
        dir.cleanup()
    except FileNotFoundError:
        pass
