
Details And Compatibility
=========================

Under the hood **pgo** simply takes advantage of LTO and PGO offered in modern
compilers. All it does is simplify the process of managing all the different
compiler types between platforms and the infrastructure for the steps to
effectivley do PGO.


Where does the profiling data go?
---------------------------------

This depends on the compiler, but it will be in either the temp or build
directory for the instrumented version of the package.


Link time optimization?
-----------------------

**pgo**, despite its name, also performs LTO. It is not possible for **pgo**
to do PGO without LTO. This is for consitency (MSVC has this limitation).

Currently there is no way to do LTO without PGO using **pgo**. If this is a
feature you wish to be supported feel free to open an issue.


What platforms/compilers are supported?
---------------------------------------

The "default" compiler for each major platform is supported. That is:

    * Linux & GCC
    * Windows & MSVC
    * Mac OS & clang
    
"Unusual" combinations like Windows & GCC very well *may* work, but are
untested. If a combination of your choice is not supported feel free to open
an issue.
