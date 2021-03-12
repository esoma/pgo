
# pgo
import pgo
# pytest
import pytest
# python
import os
# setuptools
import distutils.errors
from setuptools import Distribution
    

@pytest.mark.parametrize('dist_kwargs', [
    {},
    {"pgo": {}},
])
def test_not_available_with_no_profile_command(argv, extension, dist_kwargs):
    argv.extend(['build_profile_generate'])
    distribution = Distribution({
        "ext_modules": [extension],
        **dist_kwargs,
    })
    with pytest.raises(distutils.errors.DistutilsArgError):
        distribution.parse_command_line()


def test_default_build_dirs(argv, extension):
    argv.extend(['build_profile_generate'])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [] }
    })
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert os.path.basename(cmd.build_lib).startswith('.pgo-')
    assert os.path.basename(cmd.build_temp).startswith('.pgo-')
    

def test_set_build_dirs(argv, extension):
    argv.extend([
        'build_profile_generate',
        '--build-lib', 'build',
        '--build-temp', 'temp'
    ])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [] }
    })
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.build_lib == 'build'
    assert cmd.build_temp == 'temp'
    

def test_set_pgo_build_dirs_through_build(argv, extension):
    argv.extend([
        'build_profile_generate',
        'build',
        '--pgo-build-lib', 'build',
        '--pgo-build-temp', 'temp',
    ])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [] }
    })
    distribution.parse_command_line()
    assert len(distribution.commands) == 2
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.build_lib == 'build'
    assert cmd.build_temp == 'temp'
    
    
def test_set_build_dirs_through_build(argv, extension):
    argv.extend([
        'build_profile_generate',
        'build',
        '--build-lib', 'build',
        '--build-temp', 'temp',
    ])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [] }
    })
    distribution.parse_command_line()
    assert len(distribution.commands) == 2
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.build_lib == '.pgo-build'
    assert cmd.build_temp == '.pgo-temp'
    

