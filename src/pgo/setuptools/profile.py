
__all__ = ['profile', 'ProfileError']

# pgo
from .command import PGO_BUILD_USER_OPTIONS
from .error import ProfileError
# python
import os
import subprocess
import sys
# setuptools
from setuptools import Command


class profile(Command):

    description = 'generate profiling data for profile guided optimization'
    user_options = [
        (
            name[len("pgo-"):] if name.startswith('pgo-') else name,
            value,
            desc,
        )
        for name, value, desc in PGO_BUILD_USER_OPTIONS
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profiled = False

    def initialize_options(self):
        self.profile_command = None
        self.build_lib = None
        self.build_temp = None

    def finalize_options(self):
        self.set_undefined_options('build_profile_generate',
            ('build_lib', 'build_lib'),
            ('build_temp', 'build_temp')
        )
        self.profile_command = tuple(self.distribution.pgo["profile_command"])

    def run(self):
        if self.dry_run:
            return
        # skip running the profile if we've ran build_ext_profile_generate and
        # it didn't do anything
        if self.distribution.have_run.get('build_ext_profile_generate'):
            build_ext = self.distribution.get_command_obj(
                'build_ext_profile_generate'
            )
            if not build_ext.did_build():
                return
            
        _run_profile(self.build_lib, self.build_temp, self.profile_command)
        self.profiled = True

        
def _run_profile(build_lib, build_temp, profile_command):
    env = dict(os.environ)
    env["PGO_BUILD_LIB"] = build_lib
    env["PGO_BUILD_TEMP"] = build_temp
    env["PGO_PYTHON"] = sys.executable
    
    python_path = env.get("PYTHONPATH")
    if python_path:
        python_path = python_path.split(os.pathsep)
    else:
        python_path = []
    python_path.insert(0, build_lib)
    env["PYTHONPATH"] = os.pathsep.join(python_path)
    
    try:
        subprocess.run(profile_command, check=True, env=env)
    except FileNotFoundError as ex:
        raise ProfileError(
            f'Profile command ({" ".join(profile_command)}) '
            f'failed, the command could not be found'
        )
    except subprocess.CalledProcessError as ex:
        raise ProfileError(
            f'Profile command ({" ".join(profile_command)}) '
            f'exited with error: {ex.returncode}'
        )

