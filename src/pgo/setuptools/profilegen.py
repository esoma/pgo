
__all__ = [
    'clean_profile_generate',
    'make_build_profile_generate',
    'make_build_ext_profile_generate',
    'make_build_py_profile_generate',
]

# pgo
from .command import PGO_BUILD_USER_OPTIONS
from .compiler import (is_clang, is_msvc, _get_pgd, _get_pgort_dll,
                       _get_profdata_dir)
# python
from copy import deepcopy
import os
# setuptools
from distutils.dir_util import mkpath, remove_tree
from distutils.file_util import copy_file
from setuptools import Command


class clean_profile_generate(Command):

    description = (
        'cleanup temporary files from "build" command related to profile '
        'guided optimization'
    )
    user_options = [
        (
            name[len("pgo-"):] if name.startswith('pgo-') else name,
            value,
            desc,
        )
        for name, value, desc in PGO_BUILD_USER_OPTIONS
    ]

    def initialize_options(self):
        self.build_lib = None
        self.build_temp = None

    def finalize_options(self):
        self.set_undefined_options('clean',
            ('pgo_build_lib', 'build_lib'),
            ('pgo_build_temp', 'build_temp')
        )

    def run(self):
        try:
            remove_tree(self.build_lib, dry_run=self.dry_run)
        except FileNotFoundError:
            pass
        try:
            remove_tree(self.build_temp, dry_run=self.dry_run)
        except FileNotFoundError:
            pass


def make_build_profile_generate(base_class):

    class build_profile_generate(base_class):

        description = (
            'build everything needed to generate a profile for profile guided '
            'optimization'
        )

        def finalize_options(self):
            self.set_undefined_options('build',
                ('pgo_build_lib', 'build_lib'),
                ('pgo_build_temp', 'build_temp'),
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

    class build_ext_profile_generate(base_class):
    
        def finalize_options(self):
            self.set_undefined_options('build_profile_generate',
                ('build_lib', 'build_lib'),
                ('build_temp', 'build_temp')
            )
            super().finalize_options()
            
            
        def build_extension(self, ext):
            if ext.name in self.distribution.pgo.get("ignore_extensions", []):
                super().build_extension(ext)
            else:
                self.build_extension_with_pgo(ext)

            
        def build_extension_with_pgo(self, ext):
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
                mkpath(os.path.dirname(ext_path), dry_run=self.dry_run)
                copy_file(
                    pgort_dll, 
                    os.path.join(
                        os.path.dirname(ext_path),
                        os.path.basename(pgort_dll)
                    ),
                    dry_run=self.dry_run
                )
            elif is_clang(self.compiler):
                # clang generates ".profraw" files that then need to be 
                # combined into a single ".profdata" file later, so we specify
                # a unique directory to dump these ".profraw" files per
                # extension so that they can be recombined later in the use
                # step
                profdata_dir = _get_profdata_dir(self.build_temp)
                profile_generate_flag = f'-fprofile-generate={profdata_dir}'
                ext.extra_compile_args.append(profile_generate_flag)
                ext.extra_link_args.append(profile_generate_flag)
            else:
                ext.extra_compile_args.append('-fprofile-generate')
                ext.extra_link_args.append('-fprofile-generate')
            super().build_extension(ext)
        
    return build_ext_profile_generate


def make_build_py_profile_generate(base_class):

    class build_py_profile_generate(base_class):

        description = '"build" pure Python modules (copy to pgo directory)'

        def finalize_options(self):
            self.set_undefined_options('build_profile_generate',
                ('build_lib', 'build_lib'),
            )
            super().finalize_options()

    return build_py_profile_generate
