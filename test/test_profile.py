
# pgo
from pgo.setuptools import compiler
from pgo.setuptools.profile import ProfileError
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
def profile_command():
    return [sys.executable, '-c', 'print("hello world")']


@pytest.fixture
def distribution(profile_command):
    return Distribution({
        "pgo": { "profile_command": list(profile_command) }
    })
    

@pytest.mark.parametrize('dist_kwargs', [
    {},
    {"pgo": {}},
])
def test_not_available_with_no_profile_command(argv, dist_kwargs):
    argv.extend(['profile'])
    distribution = Distribution({
        **dist_kwargs,
    })
    with pytest.raises(distutils.errors.DistutilsArgError):
        distribution.parse_command_line()
        
        
def test_profile_command(argv, distribution, profile_command):
    argv.extend(['profile'])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert isinstance(cmd.profile_command, tuple)
    assert cmd.profile_command == tuple(profile_command)


def test_default_build_dirs(argv, distribution):
    argv.extend(['profile'])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert os.path.basename(cmd.build_lib).startswith('.pgo-')
    assert os.path.basename(cmd.build_temp).startswith('.pgo-')
    

def test_set_build_dirs(argv, distribution):
    argv.extend([
        'profile',
        '--build-lib', 'build',
        '--build-temp', 'temp'
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 1
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.build_lib == 'build'
    assert cmd.build_temp == 'temp'
    

def test_set_pgo_build_dirs_through_build_profile_generate(argv, distribution):
    argv.extend([
        'profile',
        'build_profile_generate',
        '--build-lib', 'build',
        '--build-temp', 'temp',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 2
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.build_lib == 'build'
    assert cmd.build_temp == 'temp'
    
    
def test_set_pgo_build_dirs_through_build(argv, distribution):
    argv.extend([
        'profile',
        'build',
        '--pgo-build-lib', 'build',
        '--pgo-build-temp', 'temp',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 2
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.build_lib == 'build'
    assert cmd.build_temp == 'temp'
    

def test_set_build_dirs_through_build(argv, distribution):
    argv.extend([
        'profile',
        'build',
        '--build-lib', 'build',
        '--build-temp', 'temp',
    ])
    distribution.parse_command_line()
    assert len(distribution.commands) == 2
    cmd = distribution.get_command_obj(distribution.commands[0])
    cmd.ensure_finalized()
    assert cmd.build_lib == '.pgo-build'
    assert cmd.build_temp == '.pgo-temp'
    
    
def test_run_pgo_build_lib_env(argv, pgo_lib_dir):
    argv.extend(['profile', '--build-lib', pgo_lib_dir])
    file_name = os.path.join(pgo_lib_dir, 'var')
    distribution = Distribution({ "pgo": { "profile_command": [
        sys.executable, '-c', textwrap.dedent(f"""
            import os
            with open({file_name!r}, 'w') as f:
                f.write(os.environ["PGO_BUILD_LIB"])
        """)
    ]}})
    distribution.parse_command_line()
    distribution.run_commands()
    with open(file_name) as f:
        pgo_build_lib = f.read()
    assert pgo_build_lib == pgo_lib_dir
    
    
def test_run_pgo_build_temp_env(argv, pgo_lib_dir, pgo_temp_dir):
    argv.extend(['profile', '--build-temp', pgo_temp_dir])
    file_name = os.path.join(pgo_lib_dir, 'var')
    distribution = Distribution({ "pgo": { "profile_command": [
        sys.executable, '-c', textwrap.dedent(f"""
            import os
            with open({file_name!r}, 'w') as f:
                f.write(os.environ["PGO_BUILD_TEMP"])
        """)
    ]}})
    distribution.parse_command_line()
    distribution.run_commands()
    with open(file_name) as f:
        pgo_build_temp = f.read()
    assert pgo_build_temp == pgo_temp_dir
    
    
def test_run_pgo_python_env(argv, pgo_lib_dir):
    argv.extend(['profile'])
    file_name = os.path.join(pgo_lib_dir, 'var')
    distribution = Distribution({ "pgo": { "profile_command": [
        sys.executable, '-c', textwrap.dedent(f"""
            import os
            with open({file_name!r}, 'w') as f:
                f.write(os.environ["PGO_PYTHON"])
        """)
    ]}})
    distribution.parse_command_line()
    distribution.run_commands()
    with open(file_name) as f:
        pgo_python = f.read()
    assert pgo_python == sys.executable
    
    
def test_run_pythonpath_env_outer_empty(argv, pgo_lib_dir):
    try:
        original_pythonpath = os.environ["PYTHONPATH"]
        del os.environ["PYTHONPATH"]
    except KeyError:
        original_pythonpath = None
        
    try:
        argv.extend(['profile', '--build-lib', pgo_lib_dir])
        file_name = os.path.join(pgo_lib_dir, 'var')
        distribution = Distribution({ "pgo": { "profile_command": [
            sys.executable, '-c', textwrap.dedent(f"""
                import os
                with open({file_name!r}, 'w') as f:
                    f.write(os.environ["PYTHONPATH"])
            """)
        ]}})
        distribution.parse_command_line()
        distribution.run_commands()
        with open(file_name) as f:
            pythonpath = f.read()
        assert pythonpath == pgo_lib_dir
    finally:
        if original_pythonpath is not None:
            os.environ["PYTHONPATH"] = original_pythonpath
            

def test_run_pythonpath_env_outer_has_values(argv, pgo_lib_dir, pgo_temp_dir):
    try:
        original_pythonpath = os.environ["PYTHONPATH"]
    except KeyError:
        original_pythonpath = None
    os.environ["PYTHONPATH"] = pgo_temp_dir
        
    try:
        argv.extend(['profile', '--build-lib', pgo_lib_dir])
        file_name = os.path.join(pgo_lib_dir, 'var')
        distribution = Distribution({ "pgo": { "profile_command": [
            sys.executable, '-c', textwrap.dedent(f"""
                import os
                with open({file_name!r}, 'w') as f:
                    f.write(os.environ["PYTHONPATH"])
            """)
        ]}})
        distribution.parse_command_line()
        distribution.run_commands()
        with open(file_name) as f:
            pythonpath = f.read()
        assert pythonpath == os.pathsep.join([pgo_lib_dir, pgo_temp_dir])
    finally:
        if original_pythonpath is None:
            del os.environ["PYTHONPATH"]
        else:
            os.environ["PYTHONPATH"] = original_pythonpath
            
            
def test_run_error(argv, pgo_lib_dir):
    argv.extend(['profile'])
    distribution = Distribution({ "pgo": { "profile_command": [
        sys.executable, '-c', textwrap.dedent(f"""
            import sys
            sys.exit(1)
        """)
    ]}})
    distribution.parse_command_line()
    with pytest.raises(ProfileError):
        distribution.run_commands()


def test_run_not_a_command(argv, pgo_lib_dir):
    argv.extend(['profile'])
    distribution = Distribution({ "pgo": { "profile_command": [
        os.path.join(pgo_lib_dir, 'invalid')
    ]}})
    distribution.parse_command_line()
    with pytest.raises(ProfileError):
        distribution.run_commands()
        
        
def test_dry_run(argv, pgo_lib_dir):
    argv.extend(['--dry-run', 'profile'])
    distribution = Distribution({ "pgo": { "profile_command": [
        sys.executable, '-c', textwrap.dedent(f"""
            import sys
            sys.exit(1)
        """)
    ]}})
    distribution.parse_command_line()
    distribution.run_commands()
    
    
@pytest.mark.skipif(sys.platform != 'win32', reason='not windows')
def test_run_msvc(argv, extension, pgo_lib_dir, pgo_temp_dir):
    argv.extend([
        'build_ext_profile_generate',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
        'profile',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
    ])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [
            sys.executable, '-c', 'import _pgo_test'
        ]}
    })
    distribution.parse_command_line()
    distribution.run_commands()
    # there should be a pgd file in the build directory
    build_files = os.listdir(pgo_lib_dir)
    assert [
        f for f in build_files
        if f.startswith('_pgo_test')
        if f.endswith('.pyd.pgd')
    ]
    
    
@pytest.mark.skipif(sys.platform != 'linux', reason='not linux')
def test_run_gcc(argv, extension, pgo_lib_dir, pgo_temp_dir):
    argv.extend([
        'build_ext_profile_generate',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
        'profile',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
    ])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [
            sys.executable, '-c', 'import _pgo_test'
        ]}
    })
    distribution.parse_command_line()
    distribution.run_commands()
    # there should be a _pgo_test.gcda file in the temp directory
    temp_files = [
        file
        for root, _, files in os.walk(pgo_temp_dir)
        for file in files
    ]
    assert '_pgo_test.gcda' in temp_files
    
    
@pytest.mark.skipif(sys.platform != 'darwin', reason='not macos')
def test_run_clang(argv, extension, pgo_lib_dir, pgo_temp_dir):
    argv.extend([
        'build_ext_profile_generate',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
        'profile',
        '--build-lib', pgo_lib_dir,
        '--build-temp', pgo_temp_dir,
    ])
    distribution = Distribution({
        "ext_modules": [extension],
        "pgo": { "profile_command": [
            sys.executable, '-c', 'import _pgo_test'
        ]}
    })
    distribution.parse_command_line()
    distribution.run_commands()
    # there should be a .pgo-profdatas directory in the temp directory
    temp_files = os.listdir(pgo_temp_dir)
    assert '.pgo-profdatas' in temp_files

