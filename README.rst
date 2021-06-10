========
pylibimp
========
Python utility for keeping track of packages that were imported and isolating imports.


Install
=======

.. code-block::

    pip install pylibimp


Example
=======

Normal Import Hook to save an imports dependent modules

.. code-block:: python

    import pylibimp

    with pylibimp.SaveBuiltinsImportHook() as imp:
        import pylibimp
        import urllib3

    modules = imp.get_modules()
    assert 'pylibimp' in modules
    assert 'urllib3' in modules


Import a module but keep the original system

.. code-block:: python

    import sys
    import pylibimp

    modules = sys.modules.copy()
    with pylibimp.original_system():
        import urllib3

    assert 'urllib3' not in modules
