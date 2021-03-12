
# pgo
from .profilegen import (
    make_build_profile_generate,
    make_build_ext_profile_generate,
    make_build_py_profile_generate,
)
from .profileuse import (
    make_build_profile_use,
    make_build_ext_profile_use,
)
from .build import make_build
from .profile import profile
# setuptools
from distutils.log import warn

def pgo(dist, attr, value):
    assert attr == 'pgo'
    try:
        profile_command = tuple(value["profile_command"])
    except KeyError:
        warn(
            '"pgo" option defined, but no "profile_command" -- '
            'extensions will not be built with PGO'
        )
        return
    # patch the build command to include PGO steps
    build = dist.cmdclass.get("build")
    build_ext = dist.cmdclass.get("build_ext")
    build_py = dist.cmdclass.get("build_py")
    dist.cmdclass["build_profile_generate"] = make_build_profile_generate(build)
    dist.cmdclass["build_profile_use"] = make_build_profile_use(build)
    dist.cmdclass["build_ext_profile_generate"] = make_build_ext_profile_generate(build_ext)
    dist.cmdclass["build_ext_profile_use"] = make_build_ext_profile_use(build_ext)
    dist.cmdclass["build_py_profile_generate"] = make_build_py_profile_generate(build_py)
    dist.cmdclass["profile"] = profile
    dist.cmdclass["build"] = make_build(build)