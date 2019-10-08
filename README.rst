
scipion-ed (module pwed)
===========

**scipion-ed** is the base plugin defining the Domain for Electron Diffraction image processing.


Development
-------------
Before installing **scipion-ed**, we need **scipion-pyworkflow**, so during
development one can do:

.. code-block:: bash

    # Create a clean virtual environment
    python -m venv ~/myenv
    source ~/myenv/bin/activate
    git clone git@github.com:scipion-em/scipion-pyworkflow.git
    cd scipion-pyworkflow
    python -m pip install -e .  # Install in the environment as development

    # Then we can install scipion-ed by:
    cd ..
    git clone git@github.com:scipion-ed/scipion-ed.git
    cd scipion-ed
    python -m pip install -e .  # Install in the environment as development

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

