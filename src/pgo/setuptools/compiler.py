
__all__ = ['is_clang', 'is_msvc']

# python
import os
import subprocess
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
    
    
def _get_profdata(pgo_build_lib):
    return os.path.join(pgo_build_lib, '.pgo-profdata')
    
    
def _get_profdata_dir( pgo_build_temp):
    return os.path.join(pgo_build_temp, '.pgo-profdatas')


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
