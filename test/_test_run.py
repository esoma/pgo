
# pgo
import pgo
# pytest
import pytest
# setuptools
from setuptools import Distribution, Extension


@pytest.mark.parametrize('extensions', [
    [Extension('_pgo_test', sources=['_pgo_test.c'], language='c')],
    [Extension('_pgo_test1', sources=['_pgo_test1.c'], language='c'),
     Extension('_pgo_test2', sources=['_pgo_test2.c'], language='c')]
])
def test_default(extensions, mocker):
    build_ext = pgo.make_build_ext([])
    distribution = Distribution({
        "ext_modules": extensions,
        "cmdclass": {"build_ext": build_ext},
    })
    cmd = build_ext(distribution)
    cmd.ensure_finalized()
    assert cmd.pgo_require is None
    assert cmd.pgo_disable is None
    
    build_extension = mocker.spy(cmd, 'build_extension')
    build_extension_no_pgo = mocker.patch.object(cmd, 'build_extension_no_pgo')
    build_extension_pgo_generate = mocker.patch.object(
        cmd,
        'build_extension_pgo_generate'
    )
    build_extension_pgo_use = mocker.patch.object(
        cmd,
        'build_extension_pgo_use'
    )
    profile_extensions = mocker.patch.object(cmd, 'profile_extensions')
    cmd.run()

    assert build_extension.call_count == 2 * len(extensions)
    assert build_extension_no_pgo.call_count == 0
    assert build_extension_pgo_generate.call_count == 1 * len(extensions)
    assert profile_extensions.call_count == 1
    assert build_extension_pgo_use.call_count == 1 * len(extensions)
    
    
@pytest.mark.parametrize('extensions', [
    [Extension('_pgo_test', sources=['_pgo_test.c'], language='c')],
    [Extension('_pgo_test1', sources=['_pgo_test1.c'], language='c'),
     Extension('_pgo_test2', sources=['_pgo_test2.c'], language='c')]
])
def test_default_profile_fails(extensions, mocker):
    build_ext = pgo.make_build_ext([])
    distribution = Distribution({
        "ext_modules": extensions,
        "cmdclass": {"build_ext": build_ext},
    })
    cmd = build_ext(distribution)
    cmd.ensure_finalized()
    assert cmd.pgo_require is None
    assert cmd.pgo_disable is None
    
    build_extension = mocker.spy(cmd, 'build_extension')
    build_extension_no_pgo = mocker.patch.object(cmd, 'build_extension_no_pgo')
    build_extension_pgo_generate = mocker.patch.object(
        cmd,
        'build_extension_pgo_generate'
    )
    build_extension_pgo_use = mocker.patch.object(
        cmd,
        'build_extension_pgo_use'
    )
    profile_extensions = mocker.spy(cmd, 'profile_extensions')
    cmd.run()

    assert build_extension.call_count == 2 * len(extensions)
    assert build_extension_no_pgo.call_count == 1 * len(extensions)
    assert build_extension_pgo_generate.call_count == 1 * len(extensions)
    assert profile_extensions.call_count == 1
    assert build_extension_pgo_use.call_count == 0
    
   
@pytest.mark.parametrize('extensions', [
    [Extension('_pgo_test', sources=['_pgo_test.c'], language='c')],
    [Extension('_pgo_test1', sources=['_pgo_test1.c'], language='c'),
     Extension('_pgo_test2', sources=['_pgo_test2.c'], language='c')]
])
def test_pgo_require(extensions, mocker):
    build_ext = pgo.make_build_ext([])
    distribution = Distribution({
        "ext_modules": extensions,
        "cmdclass": {"build_ext": build_ext},
    })
    cmd = build_ext(distribution)
    cmd.pgo_require = True
    cmd.ensure_finalized()
    assert cmd.pgo_require
    assert cmd.pgo_disable is None
    
    build_extension = mocker.spy(cmd, 'build_extension')
    build_extension_no_pgo = mocker.patch.object(cmd, 'build_extension_no_pgo')
    build_extension_pgo_generate = mocker.patch.object(
        cmd,
        'build_extension_pgo_generate'
    )
    build_extension_pgo_use = mocker.patch.object(
        cmd,
        'build_extension_pgo_use'
    )
    profile_extensions = mocker.patch.object(cmd, 'profile_extensions')
    cmd.run()

    assert build_extension.call_count == 2 * len(extensions)
    assert build_extension_no_pgo.call_count == 0
    assert build_extension_pgo_generate.call_count == 1 * len(extensions)
    assert profile_extensions.call_count == 1
    assert build_extension_pgo_use.call_count == 1 * len(extensions)
    

@pytest.mark.parametrize('extensions', [
    [Extension('_pgo_test', sources=['_pgo_test.c'], language='c')],
    [Extension('_pgo_test1', sources=['_pgo_test1.c'], language='c'),
     Extension('_pgo_test2', sources=['_pgo_test2.c'], language='c')]
])
def test_pgo_require_profile_fails(extensions, mocker):
    build_ext = pgo.make_build_ext([])
    distribution = Distribution({
        "ext_modules": extensions,
        "cmdclass": {"build_ext": build_ext},
    })
    cmd = build_ext(distribution)
    cmd.pgo_require = True
    cmd.ensure_finalized()
    assert cmd.pgo_require
    assert cmd.pgo_disable is None
    
    build_extension = mocker.spy(cmd, 'build_extension')
    build_extension_no_pgo = mocker.patch.object(cmd, 'build_extension_no_pgo')
    build_extension_pgo_generate = mocker.patch.object(
        cmd,
        'build_extension_pgo_generate'
    )
    build_extension_pgo_use = mocker.patch.object(
        cmd,
        'build_extension_pgo_use'
    )
    profile_extensions = mocker.spy(cmd, 'profile_extensions')
    
    with pytest.raises(pgo.PgoFailedError):
        cmd.run()

    assert build_extension.call_count == 1 * len(extensions)
    assert build_extension_no_pgo.call_count == 0
    assert build_extension_pgo_generate.call_count == 1 * len(extensions)
    assert profile_extensions.call_count == 1
    assert build_extension_pgo_use.call_count == 0
    

@pytest.mark.parametrize('extensions', [
    [Extension('_pgo_test', sources=['_pgo_test.c'], language='c')],
    [Extension('_pgo_test1', sources=['_pgo_test1.c'], language='c'),
     Extension('_pgo_test2', sources=['_pgo_test2.c'], language='c')]
])
def test_pgo_disable(extensions, mocker):
    build_ext = pgo.make_build_ext([])
    distribution = Distribution({
        "ext_modules": extensions,
        "cmdclass": {"build_ext": build_ext},
    })
    cmd = build_ext(distribution)
    cmd.pgo_disable = True
    cmd.ensure_finalized()
    assert cmd.pgo_require is None
    assert cmd.pgo_disable
    
    build_extension = mocker.spy(cmd, 'build_extension')
    build_extension_no_pgo = mocker.patch.object(cmd, 'build_extension_no_pgo')
    build_extension_pgo_generate = mocker.patch.object(
        cmd,
        'build_extension_pgo_generate'
    )
    build_extension_pgo_use = mocker.patch.object(
        cmd,
        'build_extension_pgo_use'
    )
    profile_extensions = mocker.patch.object(cmd, 'profile_extensions')
    cmd.run()

    assert build_extension.call_count == 1 * len(extensions)
    assert build_extension_no_pgo.call_count == 1 * len(extensions)
    assert build_extension_pgo_generate.call_count == 0
    assert profile_extensions.call_count == 0
    assert build_extension_pgo_use.call_count == 0
    