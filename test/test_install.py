
# pgo
import pgo
from pgo.setuptools import compiler
from pgo.setuptools.profileuse import ProfileError
# pytest
import pytest
# python
import filecmp
import os
import sys
import textwrap
# setuptools
import distutils.errors
from setuptools import Distribution


@pytest.fixture
def distribution(
    extension, extension2, cython_extension, mypyc_extension,
    py_modules, packages, package_dir, script_name
):
    return Distribution({
        "name": 'pgo_test',
        "version": '0.1.0',
        "py_modules": py_modules,
        "packages": packages,
        "package_dir": package_dir,
        "script_name": script_name,
        "ext_modules": [
            extension,
            extension2,
            cython_extension,
            mypyc_extension
        ],
        "pgo": {
            "ignore_extensions": [extension2.name],
            "profile_command": [
                sys.executable, '-c', textwrap.dedent("""
                    import _pgo_test
                    import _pgo_test_cython
                    import _pgo_test_mypyc
                """)
            ]
        }
    })
        
@pytest.mark.parametrize("extra_build_flags", [
    [],
    ['--pgo-disable'],
    ['--pgo-require'],
])
def test_run(
    extra_build_flags,
    argv, extension, extension2, cython_extension, mypyc_extension,
    lib_dir, temp_dir,
    distribution,
    py_modules, packages,
    install_dir,
):
    argv.extend([
        'install',
        '--install-lib', install_dir,
        'build',
        *extra_build_flags,
        '--build-lib', lib_dir,
        '--build-temp', temp_dir,
    ])
    distribution.parse_command_line()
    distribution.run_commands()
    # find the egg
    egg_dir = os.path.join(
        install_dir,
        [f for f in os.listdir(install_dir) if f.endswith('.egg')][0]
    )
    egg_contents = os.listdir(egg_dir)
    # extension in the installed egg is the same one as the build lib
    extension_file = [
        f for f in egg_contents
        if f.startswith(f'{extension.name}.')
        if f.endswith('.pyd') or f.endswith('.so')
    ][0]
    assert filecmp.cmp(
        os.path.join(egg_dir, extension_file),
        os.path.join(lib_dir, extension_file),
        shallow=False,
    )
    # extension2 in the installed egg is the same one as the build lib
    extension2_file = [
        f for f in egg_contents
        if f.startswith(f'{extension2.name}.')
        if f.endswith('.pyd') or f.endswith('.so')
    ][0]
    assert filecmp.cmp(
        os.path.join(egg_dir, extension2_file),
        os.path.join(lib_dir, extension2_file),
        shallow=False,
    )
    # cython_extension in the installed egg is the same one as the build lib
    cython_extension_file = [
        f for f in egg_contents
        if f.startswith(f'{cython_extension.name}.')
        if f.endswith('.pyd') or f.endswith('.so')
    ][0]
    assert filecmp.cmp(
        os.path.join(egg_dir, cython_extension_file),
        os.path.join(lib_dir, cython_extension_file),
        shallow=False,
    )
    # mypyc_extension is in the installed egg
    mypyc_extension_file = [
        f for f in egg_contents
        if f.startswith(f'{mypyc_extension.name}.')
        if f.endswith('.pyd') or f.endswith('.so')
    ][0]
    assert filecmp.cmp(
        os.path.join(egg_dir, mypyc_extension_file),
        os.path.join(lib_dir, mypyc_extension_file),
        shallow=False,
    )
    # pure python modules are installed
    for module in py_modules:
        assert f'{module}.py' in egg_contents
    # pure python packages are installed
    for package in packages:
        assert package in egg_contents
        assert '__init__.py' in os.listdir(os.path.join(egg_dir, package))
