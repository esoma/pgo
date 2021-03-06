
# pgo
import pgo
# python
import sys
# pytest
import pytest
# setuptools
import distutils.errors
import setuptools
from setuptools import Distribution, Extension


@pytest.fixture
def extension():
    return Extension('_pgo_test', sources=['_pgo_test.c'], language='c')
    
    
@pytest.fixture
def argv():
    original_argv = sys.argv
    sys.argv = ['setup.py']
    yield sys.argv
    sys.argv = original_argv


@pytest.mark.parametrize('cmd_args,pgo_require,pgo_disable', [
    ([], None, None),
    (['--pgo-require'], True, None),
    (['--pgo-disable'], None, True),
])
def test_set(argv, extension, cmd_args, pgo_require, pgo_disable):
    argv.extend(['build_ext'] + cmd_args)
    distribution = Distribution({
        "ext_modules": [extension],
        "cmdclass": {"build_ext": pgo.make_build_ext([])},
    })
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.pgo_require == pgo_require
    assert cmd.pgo_disable == pgo_disable
    if not pgo_disable:
        assert cmd.force


def test_require_and_disable_mutex(argv, extension):
    argv.extend(['build_ext', '--pgo-require', '--pgo-disable'])
    distribution = Distribution({
        "ext_modules": [extension],
        "cmdclass": {"build_ext": pgo.make_build_ext([])},
    })
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    with pytest.raises(distutils.errors.DistutilsOptionError):
        cmd.ensure_finalized()
