
def test_ImportHook():
    from pylibimp.import_hook import ImportHook

    modules = []

    imp = ImportHook()

    def save_import(name, *args, **kwargs):
        module = imp.system_import(name, *args, **kwargs)
        modules.append(name)
        return module

    imp.do_import = save_import

    with imp:
        import sys
        import collections
        import importlib

    assert 'sys' in modules
    assert 'collections' in modules
    assert 'importlib' in modules
    # There may be more modules in modules than this


def test_SaveImportHook():
    from pylibimp.import_hook import SaveImportHook

    with SaveImportHook() as imp:
        import sys
        import collections
        import importlib

    modules = imp.get_modules()
    assert 'sys' in modules
    assert 'collections' in modules
    assert 'importlib' in modules
    # There may be more modules in modules than this


def test_SaveBuiltinsImportHook():
    from pylibimp.import_hook import SaveBuiltinsImportHook

    with SaveBuiltinsImportHook() as imp:
        import sys
        import collections
        import importlib

    modules = imp.get_modules()
    assert 'sys' in modules
    assert 'collections' in modules
    assert 'importlib' in modules
    # There may be more modules in modules than this


def test_SaveImportlibImportHook():
    import importlib
    from pylibimp.import_hook import SaveImportlibImportHook

    with SaveImportlibImportHook() as imp:
        sys = importlib.import_module('sys')
        collections = importlib.import_module('collections')
        importlib = importlib.import_module('importlib')

    modules = imp.get_modules()
    assert 'sys' in modules
    assert 'collections' in modules
    assert 'importlib' in modules
    # There may be more modules in modules than this


if __name__ == '__main__':
    test_ImportHook()
    test_SaveImportHook()
    test_SaveBuiltinsImportHook()
    test_SaveImportlibImportHook()

    print('All tests passed successfully!')
