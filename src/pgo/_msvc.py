
# python
import os
import subprocess
try:
    import winreg
except ModuleNotFoundError:
    winreg = None
# setuptools
from distutils.errors import DistutilsPlatformError
from distutils.util import get_platform


def find_vc2015():
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

    
def find_vc2017():
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


# a map keyed by get_platform() return values to values accepted by
# 'vcvarsall.bat'. Always cross-compile from x86 to work with the
# lighter-weight MSVC installs that do not include native 64-bit tools
PLAT_TO_VCVARS = {
    "win32" : 'x86',
    "win-amd64" : 'x86_amd64',
    "win-arm32" : 'x86_arm',
    "win-arm64" : 'x86_arm64'
}
  
  
def get_vcvarsall():
    platform = get_platform()
    try:
        plat_spec = PLAT_TO_VCVARS[platform]
    except KeyError:
        raise DistutilsPlatformError(
            '--plat-name must be one of {}'.format(tuple(PLAT_TO_VCVARS))
        )
    path = find_vc2017()
    if not path:
        path = find_vc2015()
    if not path:
        raise DistutilsPlatformError('Unable to find vcvarsall.bat')
    return os.path.join(path, 'vcvarsall.bat'), plat_spec
