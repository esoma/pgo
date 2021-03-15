
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
def distribution(extension, extension2):
    return Distribution({
        "ext_modules": [extension, extension2],
        "pgo": {
            "ignore_extensions": [extension2.name],
            "profile_command": [
                sys.executable, '-c', 'import _pgo_test'
            ]
        }
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
    argv.extend(['build', *options])
    distribution = Distribution(dist_kwargs)
    with pytest.raises(distutils.errors.DistutilsArgError):
        distribution.parse_command_line()


def test_default_options(argv, distribution):
    argv.extend(['build'])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert os.path.basename(cmd.pgo_build_lib).startswith('.pgo-')
    assert os.path.basename(cmd.pgo_build_lib).startswith('.pgo-')
    assert not cmd.pgo_require
    assert not cmd.pgo_disable
    
    
def test_set_require(argv, distribution):
    argv.extend(['build', '--pgo-require'])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.pgo_require
    
    
def test_set_disable(argv, distribution):
    argv.extend(['build', '--pgo-disable'])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.pgo_disable
    
    
def test_set_require_and_disable(argv, distribution):
    argv.extend(['build', '--pgo-require', '--pgo-disable'])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    with pytest.raises(distutils.errors.DistutilsOptionError) as ex:
        cmd.ensure_finalized()
    

def test_set_pgo_build_dirs(argv, distribution):
    argv.extend([
        'build',
        '--pgo-build-lib', 'build',
        '--pgo-build-temp', 'temp',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.pgo_build_lib == 'build'
    assert cmd.pgo_build_temp == 'temp'
    
    
def test_set_build_dirs(argv, distribution):
    argv.extend([
        'build',
        '--build-lib', 'build',
        '--build-temp', 'temp',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.pgo_build_lib == '.pgo-build'
    assert cmd.pgo_build_temp == '.pgo-temp'


def test_run_no_profile_data_pgo_required(
    argv, extension,
    pgo_lib_dir, pgo_temp_dir,
    lib_dir, temp_dir
):
    argv.extend([
        'build',
        '--pgo-require',
        '--pgo-build-lib', pgo_lib_dir,
        '--pgo-build-temp', pgo_temp_dir,
        '--build-lib', lib_dir,
        '--build-temp', temp_dir,
    ])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": {
            "profile_command": [
                sys.executable, '-c', 'pass'
            ]
        }
    })
    distribution.parse_command_line()
    with pytest.raises(ProfileError) as ex:
        distribution.run_commands()


def test_run_no_profile_data_pgo_not_required(
    argv, extension,
    pgo_lib_dir, pgo_temp_dir,
    lib_dir, temp_dir
):
    argv.extend([
        'build',
        '--pgo-build-lib', pgo_lib_dir,
        '--pgo-build-temp', pgo_temp_dir,
        '--build-lib', lib_dir,
        '--build-temp', temp_dir,
    ])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": {
            "profile_command": [
                sys.executable, '-c', 'pass'
            ]
        }
    })
    distribution.parse_command_line()
    distribution.run_commands()
    lib_contents = os.listdir(lib_dir)
    # extension is in the build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension.name)
        if f.endswith('.pyd') or f.endswith('.so')
    ]
    
    
def test_run_no_profile_data_pgo_disabled(
    argv, extension,
    pgo_lib_dir, pgo_temp_dir,
    lib_dir, temp_dir
):
    argv.extend([
        'build',
        '--pgo-disable',
        '--pgo-build-lib', pgo_lib_dir,
        '--pgo-build-temp', pgo_temp_dir,
        '--build-lib', lib_dir,
        '--build-temp', temp_dir,
    ])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": {
            "profile_command": [
                sys.executable, '-c', 'pass'
            ]
        }
    })
    distribution.parse_command_line()
    distribution.run_commands()
    lib_contents = os.listdir(lib_dir)
    # extension is in the build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension.name)
        if f.endswith('.pyd') or f.endswith('.so')
    ]
    
    
@pytest.mark.parametrize("required", [True, False])
def test_run(
    argv, distribution, extension, extension2,
    required,
    pgo_lib_dir, pgo_temp_dir,
    lib_dir, temp_dir
):
    argv.extend([
        'build',
        '--pgo-build-lib', pgo_lib_dir,
        '--pgo-build-temp', pgo_temp_dir,
        '--build-lib', lib_dir,
        '--build-temp', temp_dir,
    ] + (['--pgo-require'] if required else []))
    distribution.parse_command_line()
    distribution.run_commands()
    lib_contents = os.listdir(lib_dir)
    lib_contents = os.listdir(pgo_lib_dir)
    # extension is in the pgo pgo build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension.name)
        if f.endswith('.pyd') or f.endswith('.so')
    ]
    # extension2 is in the pgo build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension2.name)
        if f.endswith('.pyd') or f.endswith('.so')
    ]
    if sys.platform == 'win32':
        # the pgd file is in the pgo build dir
        assert [
            f for f in lib_contents
            if f.startswith(extension.name)
            if f.endswith('.pyd.pgd')
        ]
        # the pgc file is in the pgo build dir
        assert [
            f for f in lib_contents
            if f.startswith(extension.name)
            if f.endswith('.pgc')
        ]
    elif sys.platform == 'darwin':
        # there should be a .pgo-profdata-_pgo_test directory in the pgo temp
        # directory
        temp_files = os.listdir(pgo_temp_dir)
        assert '.pgo-profdata-_pgo_test' in temp_files
    elif sys.platform == 'linux':
        # there should be a _pgo_test.gcda file in the pgo temp directory
        temp_files = [
            file
            for root, _, files in os.walk(pgo_temp_dir)
            for file in files
        ]
        assert '_pgo_test.gcda' in temp_files   
    lib_contents = os.listdir(lib_dir)
    # extension is in the build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension.name)
        if f.endswith('.pyd') or f.endswith('.so')
    ]
    # extension2 is in the build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension2.name)
        if f.endswith('.pyd') or f.endswith('.so')
    ]

    
def test_run_pgo_disabled(
    argv, distribution, extension, extension2,
    pgo_lib_dir, pgo_temp_dir,
    lib_dir, temp_dir
):
    argv.extend([
        'build',
        '--pgo-disable',
        '--pgo-build-lib', pgo_lib_dir,
        '--pgo-build-temp', pgo_temp_dir,
        '--build-lib', lib_dir,
        '--build-temp', temp_dir,
    ])
    distribution.parse_command_line()
    distribution.run_commands()
    # pgo dirs are empty
    assert not os.listdir(pgo_lib_dir)
    assert not os.listdir(pgo_temp_dir)
    lib_contents = os.listdir(lib_dir)
    # extension is in the build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension.name)
        if f.endswith('.pyd') or f.endswith('.so')
    ]
    # extension2 is in the build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension2.name)
        if f.endswith('.pyd') or f.endswith('.so')
    ]


def test_dry_run(
    argv, distribution, extension, extension2,
    pgo_lib_dir, pgo_temp_dir,
    lib_dir, temp_dir
):
    argv.extend([
        '--dry-run',
        'build',
        '--pgo-build-lib', pgo_lib_dir,
        '--pgo-build-temp', pgo_temp_dir,
        '--build-lib', lib_dir,
        '--build-temp', temp_dir,
    ])
    distribution.parse_command_line()
    distribution.run_commands()
    assert not os.listdir(pgo_lib_dir)
    assert not os.listdir(pgo_temp_dir)
    assert not os.listdir(lib_dir)
    assert not os.listdir(temp_dir)
