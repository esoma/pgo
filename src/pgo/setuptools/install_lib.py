
__all__ = ['make_install_lib']


def make_install_lib(base_class):

    class install_lib(base_class):

        user_options = base_class.user_options

        def build(self):
            if not self.skip_build:
                self.run_command('build')
                
        def get_inputs(self):
            build = self.get_finalized_command('build')
            return build.get_outputs()

    return install_lib
