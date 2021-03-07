
# pytest
import pytest
# python
import pathlib
# setuptools
from setuptools import Extension

TEST_DIR = pathlib.Path(__file__).parent.absolute()

@pytest.fixture
def extension():
    return Extension(
        '_pgo_test',
        sources=[str(TEST_DIR / '_pgo_test.c')],
        language='c'
    )
    
