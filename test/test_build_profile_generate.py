
# pgo
import pgo
# pytest
import pytest
# setuptools
import distutils.errors
from setuptools import Distribution
    

@pytest.mark.parametrize('dist_kwargs', [
    {},
    {"pgo": {}},
])
def test_not_available_with_no_profile_command(argv, extension, dist_kwargs):
    argv.extend(['build_profile_generate'])
    distribution = Distribution({
        "ext_modules": [extension],
        **dist_kwargs,
    })
    with pytest.raises(distutils.errors.DistutilsArgError):
        distribution.parse_command_line()
