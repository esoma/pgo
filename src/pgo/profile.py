
__all__ = ['profile', 'ProfileError']

# python
import os
from pathlib import Path
import subprocess
import sys
# setuptools
from distutils.errors import DistutilsExecError
from setuptools import Command


class ProfileError(DistutilsExecError):
    pass


class profile(Command):

    description = 'generate profiling data for profile guided optimization'
    user_options = []

    def initialize_options(self):
        self.profile_command = None
        self.pgo_build_lib = None
        self.pgo_build_temp = None

    def finalize_options(self):
        self.set_undefined_options('build',
            ('pgo_build_lib', 'pgo_build_lib'),
            ('pgo_build_temp', 'pgo_build_temp')
        )
        self.profile_command = tuple(self.distribution.pgo["profile_command"])

    def run(self):
        env = dict(os.environ)
        env["PGO_BUILD_LIB"] = self.pgo_build_lib
        env["PGO_BUILD_TEMP"] = self.pgo_build_temp
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
        # the pgo_build_lib at the front of it
        python_path = env.get("PYTHONPATH")
        if python_path:
            python_path.split(os.pathsep)
        else:
            python_path = []
        python_path.insert(0, self.pgo_build_lib)
        return os.pathsep.join(python_path)
