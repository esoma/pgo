
__all__ = ['make_clean']

# pgo
from .util import _dir_to_pgo_dir
# setuptools
try:
    from setuptools.command.clean import clean as _clean
except ModuleNotFoundError:
    from distutils.command.clean import clean as _clean
    
    
def make_clean(base_class):
    if base_class is None:
        base_class = _clean

    class clean(base_class):

        user_options = base_class.user_options + [
            ('pgo-build-lib=', None, 'build directory for profiling (defaults '
                                     'to build-lib prefixed with ".pgo-")'),
            ('pgo-build-temp=', None, 'temporary build directory for profiling '
                                      '(defaults to build-temp prefixed with '
                                      '".pgo-")'),
        ]

        def initialize_options(self):
            super().initialize_options()
            self.pgo_build_lib = None
            self.pgo_build_temp = None

        def finalize_options(self):
            super().finalize_options()
            if self.pgo_build_lib is None:
                self.pgo_build_lib = _dir_to_pgo_dir(self.build_lib)
            if self.pgo_build_temp is None:
                self.pgo_build_temp = _dir_to_pgo_dir(self.build_temp)

        def run(self):
            self.run_command('clean_profile_generate')
            super().run()

    return clean
