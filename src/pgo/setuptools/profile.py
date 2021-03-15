
__all__ = ['profile', 'ProfileError']

# pgo
from .command import PGO_BUILD_USER_OPTIONS
# python
import os
import subprocess
import sys
# setuptools
from distutils.errors import DistutilsExecError
from setuptools import Command


class ProfileError(DistutilsExecError):
    pass


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
        env = dict(os.environ)
        env["PGO_BUILD_LIB"] = self.build_lib
        env["PGO_BUILD_TEMP"] = self.build_temp
        env["PGO_PYTHON"] = sys.executable
        env["PYTHONPATH"] = self.generate_python_path(env)
        self.run_command(self.profile_command, env)

    def run_command(self, profile_command, env):
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

    def generate_python_path(self, env):
        # generates the appropriate PYTHONPATH for the existing environment with
        # the build_lib at the front of it
        python_path = env.get("PYTHONPATH")
        if python_path:
            python_path = python_path.split(os.pathsep)
        else:
            python_path = []
        python_path.insert(0, self.build_lib)
        return os.pathsep.join(python_path)
