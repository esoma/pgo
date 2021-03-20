#!/usr/bin/env python

# python
import pathlib
import platform
import sys
# setuptools
from setuptools import setup
from setuptools.config import read_configuration

REPO = pathlib.Path(__file__).parent.absolute()
setup_cfg = read_configuration(REPO / 'setup.cfg')

extras_require = setup_cfg["options"]["extras_require"]

# mypy doesn't work on PyPy < 3.8:
# https://github.com/python/typed_ast/issues/111
if platform.python_implementation() == 'PyPy' and sys.version_info < (3, 8):
    extras_require["test"].remove('mypy')

if __name__ == "__main__":
    setup(extras_require=extras_require)
