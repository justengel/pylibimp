
def run_normal_import_hook():
    import sys
    import pylibimp

    # Make sure urllib3 not in sys.modules to start
    if 'urllib3' in sys.modules:
        del sys.modules['urllib3']

    with pylibimp.SaveBuiltinsImportHook() as imp:
        import pylibimp
        import urllib3

    modules = imp.get_modules()
    assert 'pylibimp' in modules
    assert 'urllib3' in modules


def run_original_system():
    import sys
    import pylibimp

    # Make sure urllib3 not in sys.modules to start
    if 'urllib3' in sys.modules:
        del sys.modules['urllib3']

    modules = sys.modules.copy()
    with pylibimp.original_system():
        import urllib3

    after = sys.modules.copy()
    assert 'urllib3' not in after
    assert 'urllib3' not in modules


if __name__ == '__main__':
    run_normal_import_hook()
    run_original_system()
