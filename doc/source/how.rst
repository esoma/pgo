
How does it work?
=================

In general, profile guided optimization is the use of runtime information to
optimize static compilation. Typically the compiler must make educated guesses
about the behavior of the program in order to optimize it, but profile guided
optimization takes away (much) of that guesswork allowing for greater
performance.


The typical compilation for a Python extension is, when compared to profile 
guided optimization, composed of a **single stage** which takes the source
files and generates a shared library from them.


Profile guided optimization has **three stages**:
  #. Compile an instrumented module
  #. Use the instrumented module to generate profile data
  #. Use the profile data to generate an optimized module

**pgo** takes care of the **first** and **third** stages automatically. The
**second** stage is controlled by you, as only the developer can determine what
constitutes an appropriate set of runtime conditions to profile.

 

