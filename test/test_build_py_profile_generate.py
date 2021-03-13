
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


@pytest.fixture
def distribution(py_modules, packages, package_dir, script_name):
    return Distribution({
        "py_modules": py_modules,
        "packages": packages,
        "package_dir": package_dir,
        "script_name": script_name,
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
    argv.extend(['build_py_profile_generate'])
    distribution = Distribution({
        "py_modules": py_modules,
        "packages": packages,
        "package_dir": package_dir,
        "script_name": script_name,
        **dist_kwargs,
    })
    with pytest.raises(distutils.errors.DistutilsArgError):
        distribution.parse_command_line()


def test_default_build_dirs(argv, distribution):
    argv.extend(['build_py_profile_generate'])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert os.path.basename(cmd.build_lib).startswith('.pgo-')
    

def test_set_build_dirs(argv, distribution):
    argv.extend([
        'build_py_profile_generate',
        '--build-lib', 'build',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.build_lib == 'build'
    

def test_set_build_dirs_through_build_profile_generate(argv, distribution):
    argv.extend([
        'build_py_profile_generate',
        'build_profile_generate',
        '--build-lib', 'build',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 2
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.build_lib == 'build'
    
    
def test_set_pgo_build_dirs_through_build(argv, distribution):
    argv.extend([
        'build_py_profile_generate',
        'build',
        '--pgo-build-lib', 'build',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 2
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.build_lib == 'build'
    
    
def test_set_build_dirs_through_build(argv, distribution):
    argv.extend([
        'build_py_profile_generate',
        'build',
        '--build-lib', 'build',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 2
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.build_lib == '.pgo-build'
    

def test_run(argv, distribution, pgo_lib_dir, py_modules, packages):
    argv.extend([
        'build_py_profile_generate',
        '--build-lib', pgo_lib_dir,
    ])
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
        
        
def test_dry_run(argv, distribution, pgo_lib_dir, py_modules, packages):
    argv.extend([
        '--dry-run',
        'build_py_profile_generate',
        '--build-lib', pgo_lib_dir,
    ])
    distribution.parse_command_line()
    distribution.run_commands()
    assert not os.listdir(pgo_lib_dir)
