
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
def test_not_available_with_no_profile_command(
    argv,
    py_modules,
    packages, package_dir,
    script_name,
    dist_kwargs
):
    argv.extend(['clean_profile_generate'])
    distribution = Distribution({
        **dist_kwargs,
    })
    with pytest.raises(distutils.errors.DistutilsArgError):
        distribution.parse_command_line()
        
        
def test_default_dirs(argv, distribution):
    argv.extend(['clean_profile_generate'])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert os.path.basename(cmd.build_lib).startswith('.pgo-')
    assert os.path.basename(cmd.build_temp).startswith('.pgo-')
    

def test_set_dirs(argv, distribution):
    argv.extend([
        'clean_profile_generate',
        '--build-lib', 'build',
        '--build-temp', 'temp',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.build_lib == 'build'
    assert cmd.build_temp == 'temp'


def test_set_build_dirs_through_clean(argv, distribution):
    argv.extend([
        'clean_profile_generate',
        'clean',
        '--pgo-build-lib', 'build',
        '--pgo-build-temp', 'temp',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 2
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.build_lib == 'build'
    assert cmd.build_temp == 'temp'
    

def test_run(argv, distribution, pgo_lib_dir, pgo_temp_dir):
    argv.extend([
        'clean_profile_generate',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
    ])
    distribution.parse_command_line()
    assert os.path.isdir(pgo_lib_dir)
    assert os.path.isdir(pgo_temp_dir)
    distribution.run_commands()
    assert not os.path.isdir(pgo_lib_dir)
    assert not os.path.isdir(pgo_temp_dir)
    
    
def test_run_lib_does_not_exist(argv, distribution, pgo_lib_dir, pgo_temp_dir):
    argv.extend([
        'clean_profile_generate',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
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
        'clean_profile_generate',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
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
        'clean_profile_generate',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
    ])
    distribution.parse_command_line()
    assert os.path.isdir(pgo_lib_dir)
    assert os.path.isdir(pgo_temp_dir)
    distribution.run_commands()
    assert os.path.isdir(pgo_lib_dir)
    assert os.path.isdir(pgo_temp_dir)
