
# pgo
import pgo
# pytest
import pytest
# python
import os
import sys
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
    

def test_run(
        argv, extension,
        pgo_lib_dir, pgo_temp_dir,
        py_modules,
        packages, package_dir, script_name
    ):
    argv.extend([
        'build_profile_generate',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
    ])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [] },
        "py_modules": py_modules,
        "packages": packages,
        "package_dir": package_dir,
        "script_name": script_name,
    })
    distribution.parse_command_line()
    distribution.run_commands()
    lib_contents = os.listdir(pgo_lib_dir)
    # pure python modules are "built"
    for module in py_modules:
        assert f'{module}.py' in lib_contents
    # pure python packages are "built"
    for package in packages:
        assert package in lib_contents
        assert '__init__.py' in os.listdir(os.path.join(pgo_lib_dir, package))
    # the c-extension is in the build dir
    assert [
        f for f in lib_contents
        if f.startswith(extension.name)
        if f.endswith('.pyd') or f.endswith('.so')
    ]
    # the pgd file is in the build dir on windows, other platforms don't
    # generate anything until actually profiling
    if sys.platform == 'win32':
        assert [
            f for f in lib_contents
            if f.startswith(extension.name)
            if f.endswith('.pyd.pgd')
        ]


def test_dry_run(
        argv, extension,
        pgo_lib_dir, pgo_temp_dir,
        py_modules,
        packages, package_dir, script_name
    ):
    argv.extend([
        '--dry-run',
        'build_profile_generate',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
    ])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [] },
        "py_modules": py_modules,
        "packages": packages,
        "package_dir": package_dir,
        "script_name": script_name,
    })
    distribution.parse_command_line()
    distribution.run_commands()
    assert not os.listdir(pgo_lib_dir)
    assert not os.listdir(pgo_temp_dir)
