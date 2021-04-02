
# setuptools
from distutils.errors import DistutilsExecError


class ProfileError(DistutilsExecError):
    pass


class ProfileUseError(DistutilsExecError):
    pass