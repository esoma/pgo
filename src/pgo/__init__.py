
__all__ = ['make_build_ext']

# python
from copy import deepcopy
import enum
import os
import subprocess
# setuptools
from distutils import log
from distutils.errors import DistutilsError, DistutilsOptionError
from setuptools.command.build_ext import build_ext as _build_ext


VERSION = '0.1.1'


class _PgoMode(enum.Enum):
    NONE = object()
    GENERATE = object()
    USE = object()


def make_build_ext(profile_command, base_build_ext=_build_ext):

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
                    message = 'PGO build failed: ' + str(ex)
                    if self.pgo_require:
                        raise DistutilsError(message)
                    log.warn(message)
                    self._pgo_mode = _PgoMode.NONE
                    self._pgo_paths = []
            assert self._pgo_mode is _PgoMode.NONE
            log.info('building without PGO')
            super().build_extensions()

        def build_extension(self, ext):
            if self._pgo_mode is _PgoMode.NONE:
                super().build_extension(ext)
                return
            elif self._pgo_mode is _PgoMode.USE:
                self.build_extension_pgo_use(ext)
            else:
                assert self._pgo_mode is _PgoMode.GENERATE
                self.build_extension_pgo_generate(ext)

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

        def profile_extensions(self):
            # clean out any old profile data for msvc, otherwise it spits out
            # warnings and could have incompatible/old/bad data get profiled
            if self._is_msvc():
                for pgo_path in self._pgo_paths:
                    for file in os.listdir(pgo_path):
                        if file.endswith('.pgc'):
                            os.remove(os.path.join(pgo_path, file))
            # make sure the pure python libraries have been built so that
            # they're accessible to the profiling command
            self.run_command('build_py')
            # add the build location to the PYTHONPATH so that we import the
            # newly built stuff over anything currently installed
            env = {**os.environ}
            env["PYTHONPATH"] = os.pathsep.join(self._pgo_paths)
            
            subprocess.run(profile_command, check=True, env=env)
            
        def _is_msvc(self):
            return self.compiler.__class__.__name__ == 'MSVCCompiler'

    return BuildExtension
