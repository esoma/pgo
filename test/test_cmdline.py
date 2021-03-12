
# pgo
import pgo
# python
import os
# pytest
import pytest
# setuptools
import distutils.errors
from setuptools import Distribution
    

@pytest.mark.parametrize('cmd_args,pgo_require,pgo_disable', [
    ([], None, None),
    (['--pgo-require'], True, None),
    (['--pgo-disable'], None, True),
])
def test_require_disable(argv, extension, cmd_args, pgo_require, pgo_disable):
    argv.extend(['build', *cmd_args])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [] }
    })
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.pgo_require == pgo_require
    assert cmd.pgo_disable == pgo_disable


def test_require_and_disable_mutex(argv, extension):
    argv.extend(['build', '--pgo-require', '--pgo-disable'])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [] }
    })
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    with pytest.raises(distutils.errors.DistutilsOptionError):
        cmd.ensure_finalized()


def test_default_build_dirs(argv, extension):
    argv.extend(['build'])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [] }
    })
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.pgo_build_lib == os.path.join(
        os.path.dirname(cmd.build_lib),
        '.pgo-' + os.path.basename(cmd.build_lib)
    )
    assert cmd.pgo_build_temp == os.path.join(
        os.path.dirname(cmd.build_temp),
        '.pgo-' + os.path.basename(cmd.build_temp)
    )
    

def test_set_build_dirs_indirectly(argv, extension):
    argv.extend(['build', '--build-lib', 'build', '--build-temp', 'temp'])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [] }
    })
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.pgo_build_lib == '.pgo-build'
    assert cmd.pgo_build_temp == '.pgo-temp'
    
    
def test_set_build_dirs_directly(argv, extension):
    argv.extend([
        'build',
        '--pgo-build-lib', 'build',
        '--pgo-build-temp', 'temp'
    ])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [] }
    })
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.pgo_build_lib == 'build'
    assert cmd.pgo_build_temp == 'temp'
    
