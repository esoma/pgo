
__all__ = [
    'make_build_profile_use',
    'make_build_ext_profile_use',
]

# pgo
from .compiler import is_msvc, _get_pgd
# python
from copy import deepcopy
import os
# setuptools
try:
    from setuptools.command.build import build as _build
except ModuleNotFoundError:
    from distutils.command.build import build as _build
from setuptools.command.build_ext import build_ext as _build_ext


def make_build_profile_use(base_class):
    if base_class is None:
        base_class = _build

    class build_profile_use(base_class):

        description = (
            'build with profile guided optimization using a generated profile'
        )

        def initialize_options(self):
            super().initialize_options()
            self.pgo_build_lib = None
            self.pgo_build_temp = None

        def finalize_options(self):
            self.set_undefined_options('build',
                ('pgo_build_lib', 'pgo_build_lib'),
                ('pgo_build_temp', 'pgo_build_temp')
            )

        def get_sub_commands(self):
            commands = []
            for command in super().get_sub_commands():
                command_profile_generate = command + '_profile_use'
                if command_profile_generate in self.distribution.cmdclass:
                    command = command_profile_generate
                commands.append(command)
            return commands

    return build_profile_use


def make_build_ext_profile_use(base_class):
    if base_class is None:
        base_class = _build_ext

    class build_ext_profile_use(base_class):
    
        def initialize_options(self):
            super().initialize_options()
            self.pgo_build_lib = None
            self.pgo_build_temp = None

        def finalize_options(self):
            self.set_undefined_options('build_profile_use',
                ('pgo_build_lib', 'pgo_build_lib'),
                ('pgo_build_temp', 'pgo_build_temp')
            )
            super().finalize_options()
            
        def build_extension(self, ext):
            ext = deepcopy(ext)
            if is_msvc(self.compiler):
                # since we're building in a different directory than we profiled
                # from we need to direct the compiler to the "pgd" (and adjacent
                # "pgc" files) that we created in the pgo_build_lib directory
                ext_path = self.get_ext_fullpath(ext.name)
                pgd = _get_pgd(
                    os.path.relpath(ext_path, self.build_lib),
                    self.pgo_build_lib
                )
                ext.extra_link_args.append(f'/USEPROFILE:PGD={pgd}')
            else:
                ext.extra_compile_args.append('-fprofile-use')
                ext.extra_link_args.append('-fprofile-use')
            super().build_extension(ext)
        
    return build_ext_profile_use
