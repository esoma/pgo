
# pgo
import pgo
# pytest
import pytest
# python
import os
import shutil
import sys
# setuptools
import distutils.errors
from setuptools import Distribution


@pytest.fixture
def distribution():
    return Distribution({
        "pgo": { "profile_command": [] }
    })
    

@pytest.mark.parametrize('dist_kwargs', [
    {},
    {"pgo": {}},
])
@pytest.mark.parametrize('options', [
    ['--pgo-build-lib=.'],
    ['--pgo-build-temp=.'],
])
def test_not_wrapped_with_no_profile_command(argv, dist_kwargs, options):
    argv.extend(['clean', *options])
    distribution = Distribution({
        **dist_kwargs,
    })
    with pytest.raises(distutils.errors.DistutilsArgError):
        distribution.parse_command_line()
        

def test_default_pgo_dirs(argv, distribution):
    argv.extend(['clean'])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert os.path.basename(cmd.pgo_build_lib).startswith('.pgo-')
    assert os.path.basename(cmd.pgo_build_temp).startswith('.pgo-')


def test_set_dirs(argv, distribution):
    argv.extend([
        'clean',
        '--build-lib', 'build',
        '--build-temp', 'temp',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.pgo_build_lib == '.pgo-build'
    assert cmd.pgo_build_temp == '.pgo-temp'
    
    
def test_set_pgo_dirs(argv, distribution):
    argv.extend([
        'clean',
        '--pgo-build-lib', 'build',
        '--pgo-build-temp', 'temp',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.pgo_build_lib == 'build'
    assert cmd.pgo_build_temp == 'temp'


def test_run(argv, distribution, pgo_lib_dir, pgo_temp_dir):
    argv.extend([
        'clean',
        '--pgo-build-lib', pgo_lib_dir,
        '--pgo-build-temp', pgo_temp_dir,
    ])
    distribution.parse_command_line()
    assert os.path.isdir(pgo_lib_dir)
    assert os.path.isdir(pgo_temp_dir)
    distribution.run_commands()
    assert not os.path.isdir(pgo_lib_dir)
    assert not os.path.isdir(pgo_temp_dir)
    
    
def test_run_lib_does_not_exist(argv, distribution, pgo_lib_dir, pgo_temp_dir):
    argv.extend([
        'clean',
        '--pgo-build-lib', pgo_lib_dir,
        '--pgo-build-temp', pgo_temp_dir,
    ])
    distribution.parse_command_line()
    assert os.path.isdir(pgo_lib_dir)
    assert os.path.isdir(pgo_temp_dir)
    shutil.rmtree(pgo_lib_dir)
    distribution.run_commands()
    assert not os.path.isdir(pgo_lib_dir)
    assert not os.path.isdir(pgo_temp_dir)
    
    
def test_run_temp_does_not_exist(argv, distribution, pgo_lib_dir, pgo_temp_dir):
    argv.extend([
        'clean',
        '--pgo-build-lib', pgo_lib_dir,
        '--pgo-build-temp', pgo_temp_dir,
    ])
    distribution.parse_command_line()
    assert os.path.isdir(pgo_lib_dir)
    assert os.path.isdir(pgo_temp_dir)
    shutil.rmtree(pgo_temp_dir)
    distribution.run_commands()
    assert not os.path.isdir(pgo_lib_dir)
    assert not os.path.isdir(pgo_temp_dir)


def test_dry_run(argv, distribution, pgo_lib_dir, pgo_temp_dir):
    argv.extend([
        '--dry-run',
        'clean',
        '--pgo-build-lib', pgo_lib_dir,
        '--pgo-build-temp', pgo_temp_dir,
    ])
    distribution.parse_command_line()
    assert os.path.isdir(pgo_lib_dir)
    assert os.path.isdir(pgo_temp_dir)
    distribution.run_commands()
    assert os.path.isdir(pgo_lib_dir)
    assert os.path.isdir(pgo_temp_dir)
