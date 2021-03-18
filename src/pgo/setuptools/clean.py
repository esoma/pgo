
__all__ = ['make_clean']

# pgo
from .command import PGO_BUILD_USER_OPTIONS
from .util import _dir_to_pgo_dir
    
    
def make_clean(base_class):

    class clean(base_class):

        user_options = [*base_class.user_options, *PGO_BUILD_USER_OPTIONS]

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
