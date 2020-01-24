
scipion-ed (module pwed)
========================

**scipion-ed** is the base plugin defining the Domain for Electron Diffraction image processing.


Development
-------------

Before installing **scipion-ed**, we need **scipion-pyworkflow**, so during
development one can do:

.. code-block:: bash

    # Create a folder for the installation
    mkdir scipion-ed
    cd scipion-ed
    # Create a clean virtual environment
    python -m virtualenv --python=python3 env
    source env/bin/activate
    
    # Install pyworkflow
    git clone --branch=devel git@github.com:scipion-em/scipion-pyworkflow.git
    python -m pip install -e . scipion-pyworkflow # Install in the environment as development

    # Then we can install scipion-ed by:
    git clone git@github.com:scipion-ed/scipion-ed.git
    python -m pip install -e scipion-ed  # Install in the environment as development
    
    # And also install the plugins
    git clone git@github.com:scipion-ed/scipion-ed-dials.git
    python -m pip install -e scipion-ed-dials  # Install in the environment as development
    
    git clone git@github.com:scipion-ed/scipion-ed-xds.git
    python -m pip install -e scipion-ed-xds  # Install in the environment as development

Running tests
.............

.. code-block:: bash

    cd scipion-ed
    cd pwed/tests
    python -m unittest discover

    # To visualize the test project you need to specify SCIPION_DOMAIN and SCIPION_VERSION
    export SCIPION_DOMAIN=scipion-ed/pwed
    export SCIPION_VERSION=3.0.0

    python scipion-pyworkflow/pyworkflow/apps/pw_project.py TestEdBaseProtocols

