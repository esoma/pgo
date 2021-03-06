
# pytest
import pytest
# python
import pathlib
import sys
# setuptools
from setuptools import Extension

TEST_DIR = pathlib.Path(__file__).parent.absolute()

@pytest.fixture
def cpytoken_extension():
    if sys.version_info < (3, 8):
        include_dirs= [TEST_DIR / '_cpytoken/before-3.8']
        sources = [
            str(TEST_DIR / '_cpytoken/cpytoken.c'),
            str(TEST_DIR / '_cpytoken/before-3.8/tokenizer.c'),
        ]
    else:
        include_dirs= [TEST_DIR / '_cpytoken/3.8']
        sources = [
            str(TEST_DIR / '_cpytoken/cpytoken.c'),
            str(TEST_DIR / '_cpytoken/3.8/tokenizer.c'),
        ]
    return Extension(
        '_pgo_cpytoken',
        include_dirs=include_dirs,
        sources=sources,
        language='c'
    )
    
@pytest.fixture
def cpytoken_pydecimal_py():
    return str(TEST_DIR / '_cpytoken/_pydecimal.py')