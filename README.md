CLIClojure
=========

CLIClojure is an investigation into making a Clojure dialect that is useful for unix scripting.  An example of the usage
aimed for in CLIClojure would be to execute the following:

    #!/usr/bin/clic

    ; CLIClojure script to change permissions of some files

    (use os)

    (def files-dir "/tmp/files")

    (let [files (ls files-dir)]
      (doseq [file files]
        (chmod :+w file)))

Which would change the permissions of the files in the /tmp/files directory.  Notice that this script can be made
executable and use the shebang (#!) to run itself.  Also note the os namespace that is imported to work with standard
operating system concepts (in this case ls and chmod).  A more advanced script would be:

    #!/usr/bin/clic

    ; CLIClojure script to resize a bunch of jpgs

    (use os)

    (def images-dir "/tmp/images")

    (mkdir "thumb")

    (let [files (ls images-dir)
          images (filter (partial re-find #".*\.jpg" images))]
      (doseq [image images]
        (bin/convert :-size "120x120" image :-resize "120x120" (str "thumb/" image))))

Which would create a directory thumb and then convert all the *.jpg files in the /tmp/images directory to thumbnails and
put the thumbnail in the thumb directory.  Notice that the bin/* form calls out to a program (convert) in the underlying
operating system and passes the arguments to it.

The functional aims for this project are:
  * Build a Clojure interpreter that is as fully compatible with JVM Clojure as possible
  * Ensure it is quick enough when starting and executing to be useful for scripting tasks
  * Create good two-way communication with the underlying OS for scripting
  
Currently this project is NOT suitable for production and is still experimental - can this project achieve these aims
and is the usecase for this strong enough.  That said, the roadmap is to have something that is usable in a restricted
set of cases very soon.


Approach
========

The project is being built in Python for several reasons, firstly Python has excellent Object Oriented capabilities that
will really help to reproduce the OO Java datastructures used extensively in Clojure.  In addition developing in a
higher level language with first class functions is a good fit for a Clojure interpreter.  Python also provides good
interoperability with C so if/when speed optimisations are needed C can be brought in to help.  Finally, it has an
excellent library ecosystem to build upon.

To achieve the functional goals, the development is currently focusing on the following:

  * Building up a library of code to mirror the clojure.lang package in the JVM code base
  * Using the exact same clojure.core namespace file as JVM Clojure (although currently it is only capable of running
  the first few forms)
  * Build up the scripting libraries and functions of to enable early use


Future
======

Usefulness as a scripting language/environment is key - otherwise why not just use JVM Clojure.  This requires good
interop and good enough performance - particularly at startup.  Things I wish to investigate for this are:

  * A lot of thinking needs to be done about the right way of working with Python and the OS from within code.  The ideas
  above might need to be altered as development progresses.
  * Building a more efficient parser (possibly in C)
  * JIT interpreting of forms - only reading top level forms until they are accessed
  * Producing a "compiled" version of the libraries so that the clojure.core does not need to be read every time
  * Investigating PyPy JIT vs standard interpreted Python as the runtime

The current compatibility efforts are revolving around running increasingly more of the clojure.core namespace and
ensuring that each form works fully before moving on, however this approach will certainly not result in a fully
compatible Clojure.  There are several other things that might be done to help ensure that.  CLIClojure is not ready for
these steps yet:

  * Running some or all of the tests from JVM Clojure against CLIClojure
  * Copying the design of the JVM Clojure compiler more directly
  * Porting other projects to CLIClojure
  * Handing off to JVM Clojure if needs be


To Run
========

You need to install the Python module parsimonious using a command something like:

    sudo easy_install parsimonious

Then to run it just clone and then from within the directory type:

    CLIClojure.py

To build a binary (useful if you want to be able to use a #! to execute your script) you can use pyinstaller:

    pyinstaller CLIClojure.py

This will create a binary at:

    dist/CLIClojure/CLIClojure