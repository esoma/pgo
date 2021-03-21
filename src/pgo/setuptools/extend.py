
# pgo
from .build import make_build
from .clean import make_clean
from .install_lib import make_install_lib
from .profilegen import (
    clean_profile_generate,
    make_build_profile_generate,
    make_build_ext_profile_generate,
    make_build_py_profile_generate,
)
from .profileuse import (
    make_build_profile_use,
    make_build_ext_profile_use,
)
from .profile import profile
# setuptools
from distutils.log import warn

def pgo(dist, attr, value):
    assert attr == 'pgo'
    if "profile_command" not in value:
        warn(
            '"pgo" option defined, but no "profile_command" -- '
            'extensions will not be built with PGO'
        )
        return
    # patch the build command to include PGO steps
    build = dist.get_command_class("build")
    build_ext = dist.get_command_class("build_ext")
    build_py = dist.get_command_class("build_py")
    clean = dist.get_command_class("clean")
    install_lib = dist.get_command_class("install_lib")
    dist.cmdclass["build_profile_generate"] = make_build_profile_generate(build)
    dist.cmdclass["build_profile_use"] = make_build_profile_use(build)
    dist.cmdclass["build_ext_profile_generate"] = make_build_ext_profile_generate(build_ext)
    dist.cmdclass["build_ext_profile_use"] = make_build_ext_profile_use(build_ext)
    dist.cmdclass["build_py_profile_generate"] = make_build_py_profile_generate(build_py)
    dist.cmdclass["clean"] = make_clean(clean)
    dist.cmdclass["clean_profile_generate"] = clean_profile_generate
    dist.cmdclass["install_lib"] = make_install_lib(install_lib)
    dist.cmdclass["profile"] = profile
    dist.cmdclass["build"] = make_build(build)
