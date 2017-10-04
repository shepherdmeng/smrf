
Installation
============

SMRF relies on the Image Processing Workbench (IPW), which must be installed
first. However, IPW currently has not been tested to run natively on Windows
and must use Docker. Check the Windows section for how to run.


Install IPW
-----------

Clone `IPW here <https://github.com/USDA-ARS-NWRC/ipw>`_
.. code-block::

   git clone https://github.com/USDA-ARS-NWRC/ipw.git
   cd ipw

Carefully follow the directions described in the Install file in the top level
of the IPW folder. If you would prefer to read this file in a browser you can
also access the Install file in the repo online 'here
<https://github.com/USDA-ARS-NWRC/ipw/blob/master/Install>'_

Installing a virtualenv
-----------------------
The authors recommend using a Python `virtual environment <https://virtualenv.pypa.io/>`_ to reduce
the possibility of a dependency issue.
It is best installed via the command line using

.. code-block::
    pip install virtualenv --user

To create a virtual environment, simply change directories to where you would
like to store your environment (we recommend the same directory that smrf will
be under), and run the command
.. code-block::
  virtualenv <name of your environment>

This will create a folder named <name of your environment> in which everything
python will be installed. You must activate the environment to use it. This is
accomplished by
.. code-block::
  source <path_to_you_environment>/bin/activate>

This sets all the paths so when you pip install something it will be in that
folder. The environment is easily turned off using
.. code-block::
  deactivate

Note every instance of a terminal must turn this on to be used.


Ubuntu
------

1. Install system dependencies

   * gcc greater than 4.8
   * Python compiled with gcc

2. Ensure the following environment variables are set and readable by Python

   * $IPW, and $IPW/bin environment variable is set
   * WORKDIR, the location where temporary files are created and modified which is not default on Linux. Use /tmp for example
   * PATH, is set and readable by Python (mainly if running inside an IDE environment)
3. Activate the virtual environment

4. Install SMRF
   .. code-block::

      git clone https://github.com/USDA-ARS-NWRC/smrf
      cd smrf
      pip install -r requirements.txt
      python setup.py install

Mac OSX
-------

Mac OSX greater than 10.8 is required to run SMRF. Mac OSX comes standard with Python installed with the default
compiler clang.  To utilize multi-threading and parallel processing, gcc must be installed with Python compiled
with that gcc version.

1. MacPorts Install system dependencies

.. code-block:: bash

   port install gcc5
   port install python27

2. Or Homebrew install system dependencies

.. code-block:: python

   brew tap homebrew/versions
   brew install gcc5
   brew install python

.. note::
   Ensure that the correct gcc and Python are activated, use ``gcc --version`` and ``python --version``.
   If they are not set, use Homebrew or MacPorts activate features.

3. Ensure the following environment variables are set and readable by Python
    * $IPW, and $IPW/bin environment variable is set
    * PATH, is set and readable by Python (mainly if running inside an IDE environment)

4. Install SMRF

.. code-block:: bash

   git clone https://github.com/USDA-ARS-NWRC/smrf
   cd smrf
   pip install -r requirements.txt
   python setup.py install

Windows
-------

Since IPW has not be tested to run in Window, Docker will have to be used to run SMRF.  The docker
image can for SMRF can be found on docker hub `here <https://hub.docker.com/r/scotthavens/smrf/>`_

Testing the Install
-------------------

Test the installation with ``run_smrf test_data/testConfig.ini``, which
should run a small distribution over the Boise River Basin.
