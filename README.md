clojurePOSIX
=========

clojurePOSIX is an investigation into making a lisp to be used for unix scripting. Probably destined to join the ranks
of abandoned lisps.  The motivation for this project is twofold.  There are personal aims behind it as well as actual
functional aims for the project.

My personal aims for this project are:
  * Get to know the internals of Clojure in more depth
  * Give something back to the Clojure community either this project specifically or leveraging the knowledge gained
  from this to give back elsewhere

The functional aims for this project are:
  * Build a Clojure interpreter that is as fully compatible with JVM Clojure as possible
  * Ensure it is quick enough when starting to be used for scripting tasks
  * Create good two-way communication with POSIX/UNIX/LINUX OS for scripting
  
Currently this project is NOT suitable for production and quite likely never will be, but I'm having fun writing it so
far.  At some point I have to decide if this is a viable project in its own right to push to completion, but for now I'm
really enjoying achieving the personal aims so it's useful to me even if its not to anyone else.  Also, clojurePOSIX is
a working title and might be subject to change in the future, if I can think of something better or things change or
whatever.


Approach
========

With scripting and POSIX based goals it would seem logical to build clojurePOSIX in C, however my personal lack of
experience in C combined with the suitability of Python means clojurePOSIX is built in Python.  The python features that
will really help are OO to reproduce the Java datastructures used extensively in Clojure and first class functions to
reproduce the functional nature of the language at runtime.  In addition Python provides good interoperability with C so
if/when speed optimisations are needed C can be brought in to help.

To achieve the functional goals, the development is currently focusing on the following:

  * Building up a library of code to mirror the clojure.lang package in the JVM code base
  * Using the exact same clojure.core namespace file as JVM clojure (although currently it is only capable of running
  the first few forms)

The current development efforts are revolving around running increasingly more of the clojure.core namespace and
ensuring that each form works fully before moving on.


Future
======

The above approach will certainly not result in a fully compatible Clojure.  There are several other things that might
be done to help ensure that.  clojurePOSIX is not ready for these steps yet:

  * Running some or all of the tests from JVM Clojure against clojurePOSIX
  * Copying the design of the JVM Clojure compiler more directly
  * Porting other projects to clojurePOSIX
  * Handing off to JVM Clojure if needs be

Compatability with Clojure JVM is not the only goal of the project, usefullness as a scripting language/environment is
key - otherwise why not just use JVM Clojure.  Things I wish to investigate for this are:

  * A lot of thinking needs to be done about the right way of working with Python and POSIX from within code
  * Building a more efficient parser (possibly in C)
  * JIT interpretting of forms - only reading top level forms until they are accessed
  * Producing a "compiled" version of the libraries so that the clojure.core does not need to be read every time
  * Investigating PyPy JIT vs standard interpretted Python as the runtime

And I'm sure there are a wide variety of other problems to keep me on my toes!


To Run
========

You need to install the Python module parsimonious using a command something like:

    sudo easy_install parsimonious

Then to run it just clone and then from within the directory type:

    clojurePOSIX.py

