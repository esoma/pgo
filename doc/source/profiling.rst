
Profiling
=========

Profile guided optimization is only as good as the data that can be fed into
it. If our profiling stage doesn't reflect our most commonly used paths in
practice then we can actually cause performance to degrade. Take care to
ensure your profiling script covers a wide variety of cases.


Environment Variables
---------------------

When the profiling script is executed using the :ref:`profile` command it will
have the following environment variables available:

* **PGO_BUILD_LIB** - the directory in which the built instrumented version of
    the package resides
* **PGO_BUILD_TEMP** - the temporary directory used for building the
    instrumented version of the package
* **PGO_PYTHON** - the python executable used to execute the command

Additionally, the **PYTHONPATH** will be set such that importing any of your
modules will import the instrumented version residing in **PGO_BUILD_LIB**. 
*HOWEVER*, python will always import from the current working directory first
if it can. Depending on how your code is structured you may need to manipulate
``sys.path`` in your profile script before importing your module. For example:

.. code-block:: python

    import os
    import sys
    
    pgo_build_lib = os.environ.get("PGO_BUILD_LIB")
    if pgo_build_lib:
        sys.path.insert(0, os.path.abspath(pgo_build_lib))

    import my_module_to_profile
