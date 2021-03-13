
# pytest
import pytest
# python
import pathlib
import sys
import tempfile
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
def pgo_temp_dir():
    dir = tempfile.TemporaryDirectory()
    yield dir.name
    try:
        dir.cleanup()
    except FileNotFoundError:
        pass
