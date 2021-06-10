
def test_original_system_reset_modules_True():
    import sys
    from pylibimp.system import original_system

    # Test reset_modules=True
    modules = sys.modules.copy()
    with original_system(reset_modules=True):
        import urllib3

    after = sys.modules.copy()
    assert modules == after
    assert 'urllib3' not in after


# def test_original_system_clean_modules_False():
#     import sys
#     from pylibimp.system import original_system
#
#     # Test clean_modules=False
#     modules = sys.modules.copy()
#     with original_system(reset_modules=False, clean_modules=False):
#         import collections
#         import importlib
#         after = sys.modules.copy()
#
#     assert all(name in after for name in modules)
#     assert 'pylibimp' in after
#
#
# def test_original_system_clean_modules_True():
#     import sys
#     from pylibimp.system import original_system
#
#     # Test clean_modules=True
#     modules = sys.modules.copy()
#     with original_system(reset_modules=False, clean_modules=True):
#         import collections
#         import importlib
#         after = sys.modules.copy()
#
#     assert not all(name in after for name in modules)
#     assert 'pylibimp' not in after


def test_import_module():
    import os
    import sys
    from pylibimp.system import import_module

    this_dir = os.path.abspath(os.path.dirname(__file__))

    module = import_module(os.path.join(this_dir, 'test_import_hook.py'))
    assert hasattr(module, 'test_ImportHook')

    dependent_modules = {}
    modules = sys.modules.copy()
    module = import_module(os.path.join(this_dir, 'fake_pkg/fake_sub_pkg/mod.py'),
                           reset_modules=True, dependent_modules=dependent_modules)
    assert hasattr(module, 'VARIABLE') and module.VARIABLE == 'fake_pkg.fake_sub_pkg.mod'
    assert modules == sys.modules
    assert any('fake_pkg' in name for name in dependent_modules)


def test_get_import_chain():
    import os
    from pylibimp.system import get_import_chain

    this_dir = os.path.abspath(os.path.dirname(__file__))
    chain, path = get_import_chain(os.path.join(this_dir, '../../pylibimp/pylibimp/system.py'))
    assert chain == 'pylibimp.system'
    assert path == os.path.abspath(os.path.join(this_dir, '../../pylibimp'))


if __name__ == '__main__':
    test_original_system_reset_modules_True()
    # test_original_system_clean_modules_False()
    # test_original_system_clean_modules_True()
    test_import_module()
    test_get_import_chain()

    print('All tests passed successfully!')
