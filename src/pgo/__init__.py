
__all__ = ['make_build_ext']

# python
from copy import deepcopy
import enum
import os
import shutil
import subprocess
# setuptools
from distutils import log
from distutils.errors import DistutilsError, DistutilsOptionError
from setuptools.command.build_ext import build_ext as _build_ext
# pgo
from . import _msvc


VERSION = '0.1.2'


class _PgoMode(enum.Enum):
    NONE = object()
    GENERATE = object()
    USE = object()


def make_build_ext(profile_command, base_build_ext=_build_ext):
    profile_command = tuple(profile_command)

    class BuildExtension(base_build_ext):

        user_options = base_build_ext.user_options + [
            ('pgo-require', None, 'extension PGO is required, '
                                  'build will fail if PGO fails'),
            ('pgo-disable', None, 'extensions will not be built with PGO')
        ]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._pgo_mode = _PgoMode.NONE
            self._pgo_paths = []

        def initialize_options(self):
            super().initialize_options()
            self.pgo_require = None
            self.pgo_disable = None

        def finalize_options(self):
            super().finalize_options()
            if self.pgo_require and self.pgo_disable:
                raise DistutilsOptionError(
                    'cannot specify --pgo-require and --pgo-disable'
                )
            if not self.pgo_disable:
                self.force = True

        def build_extensions(self):
            if not self.pgo_disable:
                try:
                    self._pgo_mode = _PgoMode.GENERATE
                    assert self._pgo_paths == []
                    log.info('building with PGO instrumentation')
                    super().build_extensions()
                        
                    log.info('profiling')
                    self.profile_extensions()
                    
                    self._pgo_mode = _PgoMode.USE
                    log.info('building with PGO profile data')
                    super().build_extensions()
                    
                    self._pgo_mode = _PgoMode.NONE
                    return
                except Exception as ex:
                    self._clean_all_pgo_files()
                    message = 'PGO build failed: ' + str(ex)
                    if self.pgo_require:
                        raise PgoFailedError(message)
                    log.warn(message)
                    self._pgo_mode = _PgoMode.NONE
                    self._pgo_paths = []
            assert self._pgo_mode is _PgoMode.NONE
            log.info('building without PGO')
            super().build_extensions()

        def build_extension(self, ext):
            if self._pgo_mode is _PgoMode.NONE:
                self.build_extension_no_pgo(ext)
                return
            elif self._pgo_mode is _PgoMode.USE:
                self.build_extension_pgo_use(ext)
            else:
                assert self._pgo_mode is _PgoMode.GENERATE
                self.build_extension_pgo_generate(ext)
                
        def build_extension_no_pgo(self, ext):
            super().build_extension(ext)

        def build_extension_pgo_generate(self, ext):
            ext = deepcopy(ext)
            if self._is_msvc():
                ext.extra_compile_args.append('/GL')
                ext.extra_link_args.append('/GENPROFILE')
            else:
                ext.extra_compile_args.append('-fprofile-generate')
                ext.extra_link_args.append('-fprofile-generate')
            super().build_extension(ext)
            ext_path = self.get_ext_fullpath(ext.name)
            self._pgo_paths.append(os.path.dirname(ext_path))

        def build_extension_pgo_use(self, ext):
            ext = deepcopy(ext)
            if self._is_msvc():
                ext.extra_link_args.append('/USEPROFILE')
            else:
                ext.extra_compile_args.append('-fprofile-use')
                ext.extra_link_args.append('-fprofile-use')
            super().build_extension(ext)
            self._clean_all_pgo_files()

        def profile_extensions(self):
            temp_files = []
            try:
                command = profile_command
                self._clean_pgc_files()
                if self._is_msvc():
                    # make sure the msvc pgo runtime dll is in the same dir as
                    # the modules
                    source_pgort_dll = _msvc.get_pgort_dll()
                    for path in self._pgo_paths:
                        dest_pgort_dll = os.path.join(
                            path, os.path.basename(source_pgort_dll)
                        )
                        temp_files.append(dest_pgort_dll)
                        shutil.copyfile(source_pgort_dll, dest_pgort_dll)
                # make sure the pure python libraries have been built so that
                # they're accessible to the profiling command
                self.run_command('build_py')
                # add the build location to the PYTHONPATH so that we import
                # the newly built stuff over anything currently installed
                env = {**os.environ}
                env["PYTHONPATH"] = os.pathsep.join(self._pgo_paths)
                subprocess.run(command, check=True, env=env)
            finally:
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                    except FileNotFoundError:
                        pass
                        
        def _clean_pgc_files(self):
            if self._is_msvc():
                for pgo_path in self._pgo_paths:
                    for file in os.listdir(pgo_path):
                        if file.endswith('.pgc'):
                            os.remove(os.path.join(pgo_path, file))
                            
        def _clean_pgd_files(self):
            if self._is_msvc():
                for pgo_path in self._pgo_paths:
                    for file in os.listdir(pgo_path):
                        if file.endswith('.pgd'):
                            os.remove(os.path.join(pgo_path, file))
                            
        def _clean_all_pgo_files(self):
            self._clean_pgc_files()
            self._clean_pgd_files()
            
        def _is_msvc(self):
            return self.compiler.__class__.__name__ == 'MSVCCompiler'

    return BuildExtension

    
class PgoFailedError(DistutilsError):
    pass
