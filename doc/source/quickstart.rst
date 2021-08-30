
Quickstart
==========


Let's imagine that we have an existing project which has a Python extension
written in C called **gofast** and we want it to be as fast as possible. As
such we've decided that we don't want to leave any speed on the table and we
want to see how **pgo** can help us out.


Installation from PyPi
----------------------

In the terminal/command prompt type:

.. code-block::

    $ python -m pip install pgo
    
    
Creating a profiling script
---------------------------

The profiling script should load your extension module and put it through its
paces, so to speak. The more data you can provide the compiler, the better it
can optimize the outcome.

We'll create a ``profile.py`` script in our repository which tests the
**gofast** API over a variety of inputs:

.. code-block:: python

    import gofast
    
    for x in range(100):
        for y in range(100):
            gofast.add(x, y)
            gofast.subtract(x, y)
            gofast.multiply(x, y)
            try:
                gofast.divide(x, y)
            except ZeroDivisionError:
                pass


Configuring the build
---------------------

We need to configure our build tools to tell **pgo** how to execute our
profiling script. How to do this depends on if you're using a traditional
``setup.py`` file or the newer ``setup.cfg``. Optionally you can also add
**pgo** to your ``pyproject.toml`` build system requirements.

setup.py
^^^^^^^^

.. code-block:: python

    ...
    import sys

    setup(
        ...,
        pgo={
            "profile_command": [sys.executable, 'profile.py'],
        },
    )

setup.cfg
^^^^^^^^^

.. code-block:: ini

    ...

    [options.pgo]
        profile_command = attr: sys.executable; profile.py


Note that we used a Python script here, technically you can use whatever kind
of command you like as long as it executes your module.


pyproject.toml
^^^^^^^^^^^^^^

.. code-block:: toml

    [build-system]
    requires = ["setuptools >= 40.6.0", "wheel", "pgo"]
    build-backend = "setuptools.build_meta"


Building
--------

Building is effectivley the same as before:

.. code-block::

    $ python setup.py build
    
    