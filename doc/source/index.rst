
pgo: faster Python extensions
=============================

**pgo** seamlessly integrates profiling into the build process of Python
extensions. No need for custom build scripts or hacking
`setuptools <https://setuptools.readthedocs.io/en/latest/>`_.

Features
--------
 * increase the speed of your C, C++, Cython or mypyc extensions
 * falls back to non-pgo builds if compiler support is unavailable
 * supports Linux, Windows and MacOS
 * supports Python 3.6+ (CPython and PyPy)
 
 
User Guide
------------------
.. toctree::
    :maxdepth: 1
    
    how
    quickstart
    commands
