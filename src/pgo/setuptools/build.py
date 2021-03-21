
__all__ = ['make_build']

# pgo
from .command import PGO_BUILD_USER_OPTIONS
from .profile import ProfileError
from .util import _dir_to_pgo_dir
# setuptools
from distutils.errors import (CCompilerError, DistutilsExecError, 
                              DistutilsOptionError, DistutilsPlatformError)


def make_build(base_class):

    class build(base_class):

        user_options = base_class.user_options + [
            ('pgo-require', None, 'profile guided optimization is required, '
                                  'build will fail if environment does not '
                                  'support pgo'),
            ('pgo-disable', None, 'build without profile guided optimization'),
            *PGO_BUILD_USER_OPTIONS,
        ]

        def initialize_options(self):
            super().initialize_options()
            self.pgo_require = None
            self.pgo_disable = None
            self.pgo_build_lib = None
            self.pgo_build_temp = None

        def finalize_options(self):
            super().finalize_options()
            if self.pgo_require and self.pgo_disable:
                raise DistutilsOptionError(
                    'cannot specify --pgo-require and --pgo-disable'
                )
            if self.pgo_build_lib is None:
                self.pgo_build_lib = _dir_to_pgo_dir(self.build_lib)
            if self.pgo_build_temp is None:
                self.pgo_build_temp = _dir_to_pgo_dir(self.build_temp)

        def run(self):
            if not self.pgo_disable:
                try:
                    self.run_pgo()
                    return
                except (
                    CCompilerError,
                    DistutilsExecError,
                    DistutilsPlatformError,
                    ProfileError
                ) as ex:
                    if self.pgo_require:
                        raise
            self.run_no_pgo()

        def run_pgo(self):
            self.run_command('clean_profile_generate')
            self.run_command('build_profile_generate')
            self.run_command('profile')
            self.run_command('build_profile_use')

        def run_no_pgo(self):
            super().run()

    return build
