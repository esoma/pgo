
Commands
========

**pgo** adds several new setuptools commands and alters existing commands to
have more functionality. The new commands are seamlessly integrated into the
standard setuptools commands, but if you require finer control over your build
you may call these commands directly.


* :ref:`build`
* :ref:`build_profile_generate`
* :ref:`build_ext_profile_generate`
* :ref:`build_py_profile_generate`
* :ref:`build_profile_use`
* :ref:`build_ext_profile_use`
* :ref:`clean`
* :ref:`clean_profile_generate`
* :ref:`profile`


-------------------------------------------------------------------------------


build
-----

The standard **build** command will attempt to perform profile guided
optimization. If it fails for some reason it will default back to the normal
**build** command behavior.

When performing profile guided optimization it will automatically run the
following commands in order:

1. :ref:`build_profile_generate`
2. :ref:`profile`
3. :ref:`build_profile_use`

.. code-block:: console

    $ python setup.py build
    

pgo-require
^^^^^^^^^^^

The **pgo-require** flag requires that the build use **pgo**. If any of the 
profiling commands fail the build will simply end in an error. Note that this
flag is mutually exclusive with the :ref:`pgo-disable` flag.

.. code-block:: console
    
    $ python setup.py build --pgo-require
    
    
pgo-disable
^^^^^^^^^^^

The **pgo-disable** flag forces the build to its normal behavior. It will not
attempt to build the package with **pgo** subcommands. Note that this flag
is mutually exclusive with the :ref:`pgo-require` flag.

.. code-block:: console

    $ python setup.py build --pgo-disable
    
    
pgo-build-lib
^^^^^^^^^^^^^

The **pgo-build-lib** flag controls where the instrumented version of the
compiled extensions is built. It's equivalent to the standard **build-lib**
flag in its contents.

.. code-block:: console

    $ python setup.py build --pgo-build-lib=pgo-build/


pgo-build-temp
^^^^^^^^^^^^^^

The **pgo-build-temp** flag controls where temporary data for the instrumented
version of the compiled extensions is put. It's equivalent to the standard
**build-temp** flag in its contents.

.. code-block:: console

    $ python setup.py build --pgo-build-temp=pgo-tmp/


-------------------------------------------------------------------------------
    
    
build_profile_generate
----------------------

The **build_profile_generate** command builds the instrumented version of the
package. It executes the following special sub-commands:

1. :ref:`build_ext_profile_generate`
2. :ref:`build_py_profile_generate`

This command is typically executed by the :ref:`build` command rather than
calling it directly. Once this command has run the :ref:`profile` command may
be used.

.. code-block:: console

    $ python setup.py build_profile_generate
    
    
build-lib
^^^^^^^^^

The **build-lib** flag tells the **build_profile_generate** command where the
instrumented version of the package is to be built.

.. code-block:: console

    $ python setup.py build_profile_generate --build-lib=pgo-build/


build-temp
^^^^^^^^^^

The **build-temp** flag controls where temporary data for the instrumented
version of the compiled extensions is put.

.. code-block:: console

    $ python setup.py build_profile_generate --build-temp=pgo-tmp/
    
    
-------------------------------------------------------------------------------
    
    
build_ext_profile_generate
--------------------------

The **build_ext_profile_generate** command builds the instrumented version of
any extensions in the package.

This command is typically executed by the :ref:`build` command rather than
calling it directly.

.. code-block:: console

    $ python setup.py build_ext_profile_generate
    
    
build-lib
^^^^^^^^^

The **build-lib** flag tells the **build_ext_profile_generate** command where
the instrumented version of the package is to be built.

.. code-block:: console

    $ python setup.py build_ext_profile_generate --build-lib=pgo-build/


build-temp
^^^^^^^^^^

The **build-temp** flag controls where temporary data for the instrumented
version of the compiled extensions is put.

.. code-block:: console

    $ python setup.py build_ext_profile_generate --build-temp=pgo-tmp/
    
    
-------------------------------------------------------------------------------
    
    
build_py_profile_generate
-------------------------

The **build_py_profile_generate** command builds the instrumented version of
any pure python in the package. Effectivley this just copies that information
to the instrumented directory so that profiling can be performed.

This command is typically executed by the :ref:`build` command rather than
calling it directly.

.. code-block:: console

    $ python setup.py build_py_profile_generate
    
    
build-lib
^^^^^^^^^

The **build-lib** flag tells the **build_py_profile_generate** command where
the instrumented version of the package is to be built.

.. code-block:: console

    $ python setup.py build_py_profile_generate --build-lib=pgo-build/
    
    
-------------------------------------------------------------------------------
    
    
build_profile_use
-----------------

The **build_profile_use** command builds the profile optimized version of the 
package. It executes the special :ref:`build_ext_profile_use` sub-command.

This command is typically executed by the :ref:`build` command rather than
calling it directly.

.. code-block:: console

    $ python setup.py build_profile_use
    
    
pgo-build-lib
^^^^^^^^^^^^^

The **pgo-build-lib** flag tells the **build_profile_use** command where the
instrumented version of the package was built.

.. code-block:: console

    $ python setup.py build_profile_use --pgo-build-lib=pgo-build/


pgo-build-temp
^^^^^^^^^^^^^^

The **pgo-build-temp** flag tells the **build_profile_use** command where the
temporary data for the instrumented version of the package was put.

.. code-block:: console

    $ python setup.py build_profile_use --pgo-build-temp=pgo-tmp/
    
    
-------------------------------------------------------------------------------
    
    
build_ext_profile_use
---------------------

The **build_ext_profile_use** command builds the profile optimized version of
the extensions in the package.

This command is typically executed by the :ref:`build` command rather than
calling it directly.

.. code-block:: console

    $ python setup.py build_ext_profile_use
    
    
pgo-build-lib
^^^^^^^^^^^^^

The **pgo-build-lib** flag tells the **build_ext_profile_use** command where
the instrumented version of the package was built.

.. code-block:: console

    $ python setup.py build_ext_profile_use --pgo-build-lib=pgo-build/


pgo-build-temp
^^^^^^^^^^^^^^

The **pgo-build-temp** flag tells the **build_ext_profile_use** command where
the temporary data for the instrumented version of the package was put.

.. code-block:: console

    $ python setup.py build_ext_profile_use --pgo-build-temp=pgo-tmp/
    

-------------------------------------------------------------------------------
    
    
clean
-----

The standard **clean** command does additional cleanup against profiling data
generated by **pgo**. It now runs the :ref:`clean_profile_generate` command in
addition to its normal function.

.. code-block:: console

    $ python setup.py clean
    
    
pgo-build-lib
^^^^^^^^^^^^^

The **pgo-build-lib** flag tells the **clean** command where the instrumented
version of the compiled extension is built. Effectivley this tells the
**clean** command to remove that directory.

.. code-block:: console

    $ python setup.py clean --pgo-build-lib=pgo-build/


pgo-build-temp
^^^^^^^^^^^^^^

The **pgo-build-lib** flag tells the **clean** command where the temporary data
for the instrumented version of the compiled extension is put. Effectivley this
tells the **clean** command to remove that directory.

.. code-block:: console

    $ python setup.py clean --pgo-build-temp=pgo-tmp/
    
    
-------------------------------------------------------------------------------
    
    
clean_profile_generate
----------------------

This command cleans up only the **pgo** build and temporary directories.
Typically this is ran automatically through the `ref`:clean command.

.. code-block:: console

    $ python setup.py clean_profile_generate
    
    
pgo-build-lib
^^^^^^^^^^^^^

The **build-lib** flag tells the **clean_profile_generate** command where the
instrumented version of the compiled extension is built. Effectivley this tells
the **clean_profile_generate** command to remove that directory.

.. code-block:: console

    $ python setup.py clean_profile_generate --build-lib=pgo-build/


pgo-build-temp
^^^^^^^^^^^^^^

The **build-lib** flag tells the **clean_profile_generate** command where the
temporary data for the instrumented version of the compiled extension is put.
Effectivley this tells the **clean_profile_generate** command to remove that
directory.

.. code-block:: console

    $ python setup.py clean_profile_generate --build-temp=pgo-tmp/
    
    
-------------------------------------------------------------------------------
    
    
profile
-------

This command generates the profiling data for profile guided optimization. It
runs the profiling script specified by the author using the instrumented
version of the extensions.

.. code-block:: console

    $ python setup.py profile
    
Note that the instrumented version of the application created by
:ref:`build_profile_generate` must be available for this command to work.
Typically this is invoked through the :ref:`build` command, but if you are
tweaking your profiling script it may be useful to run this command
individually.


build-lib
^^^^^^^^^^^^^

The **build-lib** flag tells the **profile** command where the instrumented
version of the compiled extension is built.

.. code-block:: console

    $ python setup.py profile --build-lib=pgo-build/


build-temp
^^^^^^^^^^^^^^

The **pgo-build-lib** flag tells the **profile** command where the temporary
data for the instrumented version of the compiled extension is put.

.. code-block:: console

    $ python setup.py profile --build-temp=pgo-tmp/
    
