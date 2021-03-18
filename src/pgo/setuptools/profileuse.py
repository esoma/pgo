
__all__ = [
    'make_build_profile_use',
    'make_build_ext_profile_use',
]

# pgo
from .command import PGO_BUILD_USER_OPTIONS
from .compiler import (is_clang, is_msvc, _get_pgd, _get_profdata,
                       _get_profdata_dir)
from .util import _dir_to_pgo_dir
# python
from copy import deepcopy
import os
import re
import subprocess
import sys
# setuptools
from distutils.errors import CompileError, DistutilsExecError, LinkError


class ProfileError(DistutilsExecError):
    pass


def make_build_profile_use(base_class):

    class build_profile_use(base_class):

        description = (
            'build with profile guided optimization using a generated profile'
        )
        user_options = [*base_class.user_options, *PGO_BUILD_USER_OPTIONS]

        def initialize_options(self):
            super().initialize_options()
            self.pgo_build_lib = None
            self.pgo_build_temp = None

        def finalize_options(self):
            if self.pgo_build_lib is None and self.build_lib is not None:
                self.pgo_build_lib = _dir_to_pgo_dir(self.build_lib)
            if self.pgo_build_temp is None and self.build_temp is not None:
                self.pgo_build_temp = _dir_to_pgo_dir(self.build_temp)
            self.set_undefined_options('build',
                ('pgo_build_lib', 'pgo_build_lib'),
                ('pgo_build_temp', 'pgo_build_temp'),
                ('build_lib', 'build_lib'),
                ('build_temp', 'build_temp'),
            )
            super().finalize_options()

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

    class build_ext_profile_use(base_class):
    
        user_options = [*base_class.user_options, *PGO_BUILD_USER_OPTIONS]
    
        def initialize_options(self):
            super().initialize_options()
            self.pgo_build_lib = None

        def finalize_options(self):
            self.set_undefined_options('build_profile_use',
                ('pgo_build_lib', 'pgo_build_lib'),
                ('pgo_build_temp', 'build_temp'),
                ('build_lib', 'build_lib'),
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
                # since we're building in a different directory than we
                # profiled from we need to direct the compiler to the "pgd"
                # (and adjacent "pgc" files) that we created in the
                # pgo_build_lib directory
                ext_path = self.get_ext_fullpath(ext.name)
                pgd = _get_pgd(
                    os.path.relpath(ext_path, self.build_lib),
                    self.pgo_build_lib
                )
                ext.extra_link_args.append(f'/USEPROFILE:PGD={pgd}')
                # the msvc linker will produce a warning if there are no pgc
                # files (the actual profiling data) for a given pgd, but there
                # is no way to turn that into an error, so we'll need to search
                # ourselves to make sure they exist
                if not self.dry_run:
                    pgd_dirname = os.path.dirname(pgd)
                    pgd_name = os.path.splitext(os.path.basename(pgd))[0]
                    pgc_pattern = re.compile(
                        '^' + re.escape(pgd_name) + r'\!\d+\.pgc$'
                    )
                    try:
                        pgd_dir_files = os.listdir(pgd_dirname)
                    except FileNotFoundError:
                        pgd_dir_files = []
                    for file in pgd_dir_files:
                        if pgc_pattern.match(file):
                            break
                    else:
                        raise ProfileError(
                            f'No .PCG matching "{pgd_name}!*.pgc" in '
                            f'{pgd_dirname}'
                        )
            elif is_clang(self.compiler):
                # we need to combine the ".profraw" files that clang generates
                # into a ".profdata" file
                profdata_dir = _get_profdata_dir(self.build_temp)
                profdata = _get_profdata(self.pgo_build_lib)
                if not self.dry_run:
                    # all the ".profraw" files for this extension should be in
                    # the profdata_dir that we specified in the generate step
                    try:
                        profraws = [
                            os.path.join(profdata_dir, raw)
                            for raw in os.listdir(profdata_dir)
                            if raw.endswith('.profraw')
                        ]
                    except FileNotFoundError as ex:
                        raise ProfileError(ex)
                    # llvm-profdata will merge our ".profraw" data into the
                    # correct ".profdata" file we need
                    llvm_profdata_merge = [
                        'llvm-profdata', 'merge',
                        f'-output={profdata}',
                        *profraws
                    ]
                    if sys.platform == 'darwin':
                        # on macs the llvm-profdata command isn't normally on
                        # the path, so run it through xcrun
                        llvm_profdata_merge.insert(0, 'xcrun')
                    try:
                        subprocess.run(llvm_profdata_merge, check=True)
                    except subprocess.CalledProcessError as ex:
                        raise ProfileError(ex)
                profile_use_flag = f'-fprofile-use={profdata}'
                ext.extra_compile_args.append(profile_use_flag)
                ext.extra_link_args.append(profile_use_flag)
            else:
                ext.extra_compile_args.extend([
                    '-fprofile-use',
                    '-Werror=missing-profile',
                ])
                ext.extra_link_args.extend([
                    '-fprofile-use',
                    '-Werror=missing-profile',
                ])
            try:
                super().build_extension(ext)
            except (CompileError, LinkError) as ex:
                raise ProfileError(ex)
        
    return build_ext_profile_use
