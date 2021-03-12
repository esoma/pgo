
__all__ = [
    'make_build_profile_generate',
    'make_build_ext_profile_generate',
    'make_build_py_profile_generate',
]

# pgo
from .compiler import is_msvc, _get_pgd, _get_pgort_dll
# python
from copy import deepcopy
import os
import shutil
# setuptools
try:
    from setuptools.command.build import build as _build
except ModuleNotFoundError:
    from distutils.command.build import build as _build
from setuptools.command.build_ext import build_ext as _build_ext
from setuptools.command.build_py import build_py as _build_py


def make_build_profile_generate(base_class):
    if base_class is None:
        base_class = _build

    class build_profile_generate(base_class):

        description = (
            'build everything needed to generate a profile for profile guided '
            'optimization'
        )

        def finalize_options(self):
            self.set_undefined_options('build',
                ('pgo_build_lib', 'build_lib'),
                ('pgo_build_temp', 'build_temp')
            )
            super().finalize_options()

        def get_sub_commands(self):
            commands = []
            for command in super().get_sub_commands():
                command_profile_generate = command + '_profile_generate'
                if command_profile_generate in self.distribution.cmdclass:
                    command = command_profile_generate
                commands.append(command)
            return commands

    return build_profile_generate


def make_build_ext_profile_generate(base_class):
    if base_class is None:
        base_class = _build_ext

    class build_ext_profile_generate(base_class):
    
        def finalize_options(self):
            self.set_undefined_options('build_profile_generate',
                ('build_lib', 'build_lib'),
                ('build_temp', 'build_temp')
            )
            super().finalize_options()
            
        def build_extension(self, ext):
            ext = deepcopy(ext)
            if is_msvc(self.compiler):
                # since we're profiling in a different directory than we're
                # building we need to direct the compiler to the "pgd" (and
                # adjacent "pgc" files) to use, to do that properly we need to
                # explicitly name our "pgd" file
                ext_path = self.get_ext_fullpath(ext.name)
                pgd = _get_pgd(
                    os.path.relpath(ext_path, self.build_lib),
                    self.build_lib
                )
                ext.extra_compile_args.append('/GL')
                ext.extra_link_args.append(f'/GENPROFILE:PGD={pgd}')
                # the pgo runtime dll is required when /GENPROFILE is applied,
                # since this is a dev lib it's not normally on the path and 
                # because of Python's DLL import rules in 3.8 there isn't an
                # easy way to just add it to the importable path, so we'll copy
                # it next to the extension that we build
                pgort_dll = _get_pgort_dll()
                shutil.copyfile(
                    pgort_dll,
                    os.path.join(
                        os.path.dirname(ext_path),
                        os.path.basename(pgort_dll)
                    )
                )
            else:
                ext.extra_compile_args.append('-fprofile-generate')
                ext.extra_link_args.append('-fprofile-generate')
            super().build_extension(ext)
        
    return build_ext_profile_generate


def make_build_py_profile_generate(base_class):
    if base_class is None:
        base_class = _build_py

    class build_py_profile_generate(base_class):

        description = '"build" pure Python modules (copy to pgo directory)'

        def finalize_options(self):
            self.set_undefined_options('build_profile_generate',
                ('build_lib', 'build_lib'),
            )
            super().finalize_options()

    return build_py_profile_generate