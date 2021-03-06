
# pgo
import pgo
# pytest
import pytest
# python
import os
import re
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


def test_python_path_set(cpytoken_extension, temp_dir, mocker):
    build_ext = pgo.make_build_ext([
        sys.executable,
        '-c', textwrap.dedent("""
        import sys
        if len(sys.path) < 2 or sys.path[0] != '' or sys.path[1] != {!r}:
            raise ValueError(sys.path)
        """.format(temp_dir))
    ])
    distribution = Distribution({
        "ext_modules": [cpytoken_extension],
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
    
    
def test_can_import(cpytoken_extension):
    with pytest.raises(ImportError):
        import _pgo_test
        
    build_ext = pgo.make_build_ext([
        sys.executable, '-c', 'import _pgo_cpytoken'
    ])
    distribution = Distribution({
        "ext_modules": [cpytoken_extension],
        "cmdclass": {"build_ext": build_ext},
    })
    cmd = build_ext(distribution)
    cmd.pgo_require = True
    cmd.ensure_finalized()
    assert cmd.pgo_require
    assert cmd.pgo_disable is None
    
    cmd.run()
    
    
def test_does_optimize(cpytoken_extension, cpytoken_pydecimal_py):
    with pytest.raises(ImportError):
        import _pgo_test
        
    bench_command = textwrap.dedent("""
    import _pgo_cpytoken
    import timeit
    with open({!r}, 'rb') as f:
        d = f.read()
    print(timeit.timeit(
        'for t in _pgo_cpytoken.tokenize(d): pass',
        number=1000,
        globals=globals()
    ))
    """.format(cpytoken_pydecimal_py))
        
    build_ext = pgo.make_build_ext([sys.executable, '-c', textwrap.dedent("""
    import _pgo_cpytoken
    with open({!r}, 'rb') as f:
        d = f.read()
    for i in range(100):
        for t in _pgo_cpytoken.tokenize(d):
            pass
    """.format(cpytoken_pydecimal_py))])
    distribution = Distribution({
        "ext_modules": [cpytoken_extension],
        "cmdclass": {"build_ext": build_ext},
    })
    
    # build without pgo
    cmd = build_ext(distribution)
    cmd.force = True
    cmd.pgo_disable = True
    cmd.ensure_finalized()
    cmd.run()
    outdir = os.path.dirname(cmd.get_ext_fullpath(cpytoken_extension.name))
    env = {**os.environ}
    env["PYTHONPATH"] = outdir
    res = subprocess.run(
        [sys.executable, '-c', bench_command],
        check=True,
        env=env,
        stdout=subprocess.PIPE,
    )
    no_pgo_time = float(res.stdout.decode('utf8'))
    
    # build with pgo
    cmd = build_ext(distribution)
    cmd.force = True
    cmd.pgo_require = True
    cmd.ensure_finalized()
    cmd.run()
    outdir = os.path.dirname(cmd.get_ext_fullpath(cpytoken_extension.name))
    env = {**os.environ}
    env["PYTHONPATH"] = outdir
    res = subprocess.run(
        [sys.executable, '-c', bench_command],
        check=True,
        env=env,
        stdout=subprocess.PIPE,
    )
    pgo_time = float(res.stdout.decode('utf8'))
    
    # check for at least a 5% speed decrease
    print(pgo_time, no_pgo_time)
    assert pgo_time < (no_pgo_time * .95)
