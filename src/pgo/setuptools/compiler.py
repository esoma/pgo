
__all__ = ['is_clang', 'is_msvc']

# pgo
from .error import ProfileError, ProfileUseError
from .profile import _run_profile
# python
import functools
import os
from pathlib import Path
import subprocess
import sys
try:
    import winreg
except ModuleNotFoundError:
    winreg = None
# setuptools
from distutils.ccompiler import CCompiler, new_compiler
from distutils.errors import DistutilsPlatformError
from distutils.util import get_platform


def is_msvc(compiler):
    if not isinstance(compiler, CCompiler):
        compiler = new_compiler(compiler=compiler)
    return compiler.compiler_type == 'msvc'
    
    
def is_clang(compiler):
    if not isinstance(compiler, CCompiler):
        compiler = new_compiler(compiler=compiler)
    if compiler.compiler_type == 'unix':
        cc = compiler.compiler[0]
        out = subprocess.run(
            [cc],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return out.stderr.startswith(b'clang:')
    return False
    
    
def _get_pgd(rel_ext_path, pgo_build_lib):
    return os.path.join(pgo_build_lib, f'{rel_ext_path}.pgd')
    
    
def _get_profdata_dir(pgo_build_temp):
    return os.path.join(pgo_build_temp, '.pgo-profdatas')
    
    
def _merge_profdata(dry_run, pgo_build_lib, pgo_build_temp, extension):
    profdata = os.path.join(pgo_build_lib, f'.pgo-profdata-{extension.name}')
    if dry_run:
        return profdata
    # all of the clang profile data is built in the same directory without 
    # any real distinguishing features
    #
    # this presents a problem when multiple extensions are being profiled,
    # because we need to direct the extension to the profile data specifically
    # belonging to it
    #
    # in order to figure that out we'll just import the instrumented extension,
    # which should update the mtime of the profile data, then we know that the
    # latest updated profile is the one for this extension
    profdata_dir = _get_profdata_dir(pgo_build_temp)
    try:
        profraws = set(Path(profdata_dir).iterdir())
    except FileNotFoundError:
        profraws = set()
    try:
        _run_profile(
            pgo_build_lib,
            pgo_build_temp,
            [sys.executable, '-c', f'import {extension.name}']
        )
    except ProfileError as ex:
        raise ProfileUseError(ex)
    try:
        profraw = sorted(
            Path(profdata_dir).iterdir(),
            key=os.path.getmtime
        )[-1]
    except IndexError:
        raise ProfileUseError(f'missing profile data for {extension.name}')
    # it's possible there is a problem with the actual profiling script that
    # prevents it from generating the profile data, so we might just be
    # creating a dummy profraw, make sure it existed before we ran our little
    # hack
    if profraw not in profraws:
        raise ProfileUseError(f'missing profile data for {extension.name}')
    # llvm-profdata will merge our profraw data into the correct profdata file
    # we need
    llvm_profdata_merge = [
        'llvm-profdata', 'merge',
        f'-output={profdata}',
        profraw
    ]
    if sys.platform == 'darwin':
        # on macs the llvm-profdata command isn't normally on
        # the path, so run it through xcrun
        llvm_profdata_merge.insert(0, 'xcrun')
    try:
        subprocess.run(llvm_profdata_merge, check=True)
    except subprocess.CalledProcessError as ex:
        raise ProfileUseError(ex)
    return profdata


@functools.cache
def _get_pgort_dll():
    out = subprocess.check_output([
        'cmd', '/u', '/c', *_get_vcvarsall(), '>nul', '2>nul',
        '&&',
        'set', 'path',
    ]).decode('utf-16le')
    path = [
        l for l in out.splitlines()
        if l.lower().startswith('path=')
    ][0][len('path='):]
    for path in path.split(';'):
        try:
            for file in os.listdir(path):
                if file == 'pgort140.dll':
                    return os.path.join(path, file)
        except FileNotFoundError:
            pass
        except OSError:
            pass
    raise DistutilsPlatformError('Unable to find pgort140.dll')


def _get_vcvarsall():
    PLAT_TO_VCVARS = {
        "win32" : 'x86',
        "win-amd64" : 'amd64',
        "win-arm32" : 'arm',
        "win-arm64" : 'arm64'
    }
    try:
        arch = PLAT_TO_VCVARS[get_platform()]
    except KeyError:
        raise DistutilsPlatformError(
            '--plat-name must be one of {}'.format(tuple(PLAT_TO_VCVARS))
        )

    path = _find_vc2017()
    if not path:
        path = _find_vc2015()
    if not path:
        raise DistutilsPlatformError('Unable to find vcvarsall.bat')
        
    return os.path.join(path, 'vcvarsall.bat'), arch


def _find_vc2015():
    # this was roughly copied from distutils._msvccompiler
    if not winreg:
        return None
    try:
        key = winreg.OpenKeyEx(
            winreg.HKEY_LOCAL_MACHINE,
            r'Software\Microsoft\VisualStudio\SxS\VC7',
            access=winreg.KEY_READ | winreg.KEY_WOW64_32KEY
        )
    except OSError:
        return None
    best_version = 0
    best_dir = None
    with key:
        for i in count():
            try:
                v, vc_dir, vt = winreg.EnumValue(key, i)
            except OSError:
                break
            if v and vt == winreg.REG_SZ and os.path.isdir(vc_dir):
                try:
                    version = int(float(v))
                except (ValueError, TypeError):
                    continue
                if version >= 14 and version > best_version:
                    best_version, best_dir = version, vc_dir
    return best_dir
    
    
def _find_vc2017():
    # this was roughly copied from distutils._msvccompiler
    root = (
        os.environ.get('ProgramFiles(x86)') or
        os.environ.get('ProgramFiles')
    )
    if not root:
       return None 
    try:
        path = subprocess.check_output([
            os.path.join(
                root,
                'Microsoft Visual Studio',
                'Installer',
                'vswhere.exe'
            ),
            '-latest',
            '-prerelease',
            '-requires', 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64',
            '-property', 'installationPath',
            '-products', '*',
        ], encoding='mbcs', errors='strict').strip()
    except (subprocess.CalledProcessError, OSError, UnicodeDecodeError):
        return None
    path = os.path.join(path, 'VC', 'Auxiliary', 'Build')
    if os.path.isdir(path):
        return path
    return None
