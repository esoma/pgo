
# pgo
import pgo
from pgo import compiler
from pgo.profileuse import ProfileError
# pytest
import pytest
# python
import os
import sys
import textwrap
# setuptools
import distutils.errors
from setuptools import Distribution


@pytest.fixture
def distribution(extension):
    return Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [] }
    })
    

@pytest.mark.parametrize('dist_kwargs', [
    {},
    {"pgo": {}},
])
def test_not_available_with_no_profile_command(argv, extension, dist_kwargs):
    argv.extend(['build_profile_use'])
    distribution = Distribution({
        "ext_modules": [extension],
        **dist_kwargs,
    })
    with pytest.raises(distutils.errors.DistutilsArgError):
        distribution.parse_command_line()


def test_default_pgo_build_dirs(argv, distribution):
    argv.extend(['build_profile_use'])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert os.path.basename(cmd.pgo_build_lib).startswith('.pgo-')
    assert os.path.basename(cmd.pgo_build_lib).startswith('.pgo-')
    

def test_set_pgo_build_dirs(argv, distribution):
    argv.extend([
        'build_profile_use',
        '--pgo-build-lib', 'build',
        '--pgo-build-temp', 'temp',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.pgo_build_lib == 'build'
    assert cmd.pgo_build_temp == 'temp'
    

def test_set_pgo_build_dirs_through_build(argv, distribution):
    argv.extend([
        'build_profile_use',
        'build',
        '--pgo-build-lib', 'build',
        '--pgo-build-temp', 'temp',
        '--build-temp', 'temp2',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 2
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.pgo_build_lib == 'build'
    assert cmd.pgo_build_temp == 'temp'
    
    
def test_set_build_dirs_through_build(argv, distribution):
    argv.extend([
        'build_profile_use',
        'build',
        '--build-lib', 'build',
        '--build-temp', 'temp',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 2
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.pgo_build_lib == '.pgo-build'
    assert cmd.pgo_build_temp == '.pgo-temp'


def test_run_no_profile_data(
    argv, distribution,
    pgo_lib_dir, pgo_temp_dir,
    lib_dir, temp_dir
):
    argv.extend([
        'build_profile_use',
        '--pgo-build-lib', pgo_lib_dir,
        '--build-lib', lib_dir,
        '--build-temp', temp_dir,
    ])
    distribution.parse_command_line()
    with pytest.raises(ProfileError):
        distribution.run_commands()
        

@pytest.mark.skipif(sys.platform != 'win32', reason='not windows')
def test_run_windows(
    argv, extension, extension2,
    pgo_lib_dir, pgo_temp_dir,
    lib_dir, temp_dir
):
    argv.extend([
        'build_ext_profile_generate',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
        'profile',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
        'build_profile_use',
        '--pgo-build-lib', pgo_lib_dir,
        '--pgo-build-temp', pgo_temp_dir,
        '--build-lib', lib_dir,
        '--build-temp', temp_dir,
    ])
    distribution = Distribution({
        "ext_modules": [extension, extension2],
        "pgo": {
            "ignore_extensions": [extension2.name],
            "profile_command": [sys.executable, '-c', 'import _pgo_test'],
        }
    })
    distribution.parse_command_line()
    distribution.run_commands()
    lib_contents = os.listdir(lib_dir)
    # extension is in the build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension.name)
        if f.endswith('.pyd')
    ]
    # extension2 is in the build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension2.name)
        if f.endswith('.pyd')
    ]
    # no pgd file is not in the build dir
    assert not [
        f for f in lib_contents
        if f.endswith('.pyd.pgd')
    ]
    
@pytest.mark.skipif(sys.platform == 'win32', reason='windows')
def test_run_not_windows(
    argv, extension, extension2,
    pgo_lib_dir, pgo_temp_dir,
    lib_dir, temp_dir
):
    argv.extend([
        'build_ext_profile_generate',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
        'profile',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
        'build_profile_use',
        '--pgo-build-lib', pgo_lib_dir,
        '--pgo-build-temp', pgo_temp_dir,
        '--build-lib', lib_dir,
        '--build-temp', pgo_temp_dir,
    ])
    distribution = Distribution({
        "ext_modules": [extension, extension2],
        "pgo": {
            "ignore_extensions": [extension2.name],
            "profile_command": [sys.executable, '-c', 'import _pgo_test'],
        }
    })
    distribution.parse_command_line()
    distribution.run_commands()
    lib_contents = os.listdir(lib_dir)
    # extension is in the build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension.name)
        if f.endswith('.so')
    ]
    # extension2 is in the build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension2.name)
        if f.endswith('.so')
    ]
    # the gcda (gcc) and profdata (clang) files are not in the build dir
    assert not [
        f for f in lib_contents
        if f.endswith('.gcda') or f.endswith('.profdata')
    ]


def test_dry_run(argv, distribution, pgo_lib_dir, pgo_temp_dir):
    argv.extend([
        '--dry-run',
        'build_profile_use',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
    ])
    distribution.parse_command_line()
    distribution.run_commands()
    assert not os.listdir(pgo_lib_dir)
    assert not os.listdir(pgo_temp_dir)
