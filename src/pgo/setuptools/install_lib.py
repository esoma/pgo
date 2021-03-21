
__all__ = ['make_install_lib']


def make_install_lib(base_class):

    class install_lib(base_class):

        user_options = base_class.user_options

        def build(self):
            if not self.skip_build:
                self.run_command('build')

    return install_lib
