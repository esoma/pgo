
# pgo
import pgo
from pgo import compiler
# pytest
import pytest
# python
import os
import sys
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
    argv.extend(['build_ext_profile_generate'])
    distribution = Distribution({
        "ext_modules": [extension],
        **dist_kwargs,
    })
    with pytest.raises(distutils.errors.DistutilsArgError):
        distribution.parse_command_line()


def test_default_build_dirs(argv, distribution):
    argv.extend(['build_ext_profile_generate'])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    # for msvc the build_temp directory has Release/Debug attached to it
    if compiler.is_msvc(cmd.compiler):
        build_temp = os.path.dirname(cmd.build_temp)
    else:
        build_temp = cmd.build_temp
    assert os.path.basename(cmd.build_lib).startswith('.pgo-')
    assert os.path.basename(build_temp).startswith('.pgo-')
    

def test_set_build_dirs(argv, distribution):
    argv.extend([
        'build_ext_profile_generate',
        '--build-lib', 'build',
        '--build-temp', 'temp'
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    # for msvc the build_temp directory has Release/Debug attached to it
    if compiler.is_msvc(cmd.compiler):
        build_temp = os.path.dirname(cmd.build_temp)
    else:
        build_temp = cmd.build_temp
    assert cmd.build_lib == 'build'
    assert build_temp == 'temp'
    

def test_set_pgo_build_dirs_through_build_profile_generate(argv, distribution):
    argv.extend([
        'build_ext_profile_generate',
        'build_profile_generate',
        '--build-lib', 'build',
        '--build-temp', 'temp',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 2
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    # for msvc the build_temp directory has Release/Debug attached to it
    if compiler.is_msvc(cmd.compiler):
        build_temp = os.path.dirname(cmd.build_temp)
    else:
        build_temp = cmd.build_temp
    assert cmd.build_lib == 'build'
    assert build_temp == 'temp'
    
    
def test_set_pgo_build_dirs_through_build(argv, distribution):
    argv.extend([
        'build_ext_profile_generate',
        'build',
        '--pgo-build-lib', 'build',
        '--pgo-build-temp', 'temp',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 2
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    # for msvc the build_temp directory has Release/Debug attached to it
    if compiler.is_msvc(cmd.compiler):
        build_temp = os.path.dirname(cmd.build_temp)
    else:
        build_temp = cmd.build_temp
    assert cmd.build_lib == 'build'
    assert build_temp == 'temp'
    
    
def test_set_build_dirs_through_build(argv, distribution):
    argv.extend([
        'build_ext_profile_generate',
        'build',
        '--build-lib', 'build',
        '--build-temp', 'temp',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 2
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    # for msvc the build_temp directory has Release/Debug attached to it
    if compiler.is_msvc(cmd.compiler):
        build_temp = os.path.dirname(cmd.build_temp)
    else:
        build_temp = cmd.build_temp
    assert cmd.build_lib == '.pgo-build'
    assert build_temp == '.pgo-temp'

    
@pytest.mark.skipif('MSC' not in sys.version, reason='not built with msvc')
def test_run(argv, distribution, pgo_lib_dir, pgo_temp_dir, extension):
    argv.extend([
        'build_ext_profile_generate',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
    ])
    distribution.parse_command_line()
    distribution.run_commands()
    lib_contents = os.listdir(pgo_lib_dir)
    # the c-extension is in the build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension.name)
        if f.endswith('.pyd')
    ]
    # the pgd file is in the build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension.name)
        if f.endswith('.pyd.pgd')
    ]


def test_dry_run(argv, distribution, pgo_lib_dir, pgo_temp_dir, extension):
    argv.extend([
        '--dry-run',
        'build_ext_profile_generate',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
    ])
    distribution.parse_command_line()
    distribution.run_commands()
    assert not os.listdir(pgo_lib_dir)
    assert not os.listdir(pgo_temp_dir)
