
# pgo
import pgo
# pytest
import pytest
# python
import json
import os
import subprocess
import sys
import tempfile
import textwrap
# setuptools
from setuptools import Distribution, Extension
    
    
@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


def test_python_path_set(extension, temp_dir, mocker):
    build_ext = pgo.make_build_ext([
        sys.executable,
        '-c', textwrap.dedent("""
        import sys
        if len(sys.path) < 2 or sys.path[0] != '' or sys.path[1] != {!r}:
            raise ValueError(sys.path)
        """.format(temp_dir))
    ])
    distribution = Distribution({
        "ext_modules": [extension],
        "cmdclass": {"build_ext": build_ext},
    })
    cmd = build_ext(distribution)
    cmd.pgo_require = True
    cmd.ensure_finalized()
    assert cmd.pgo_require
    assert cmd.pgo_disable is None
    
    def _(ext):
        cmd._pgo_paths = [temp_dir]
    mocker.patch.object(cmd, 'build_extension_pgo_generate', new=_)
    build_extension = mocker.spy(cmd, 'build_extension')
    build_extension_pgo_use = mocker.patch.object(
        cmd,
        'build_extension_pgo_use'
    )
    cmd.run()
    

def test_can_import(extension):
    with pytest.raises(ModuleNotFoundError):
        import _pgo_cpytoken
        
    build_ext = pgo.make_build_ext([
        sys.executable, '-c', 'import sys; print(sys.path); import _pgo_test'
    ])
    distribution = Distribution({
        "ext_modules": [extension],
        "cmdclass": {"build_ext": build_ext},
    })
    cmd = build_ext(distribution)
    cmd.pgo_require = True
    cmd.ensure_finalized()
    assert cmd.pgo_require
    assert cmd.pgo_disable is None
    
    cmd.run()
