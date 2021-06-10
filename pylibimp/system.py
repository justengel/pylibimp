import os.path
import sys
import contextlib
from .import_hook import SaveImportHook, DefaultHook

__all__ = ['original_system', 'import_module', 'get_import_chain']


@contextlib.contextmanager
def original_system(new_path=None, reset_modules=True, **kwargs):
    """Context manager to reset sys.path and sys.modules to the previous state before the context operation.

    Args:
        new_path (str)[None]: Temporarily add a path to sys.path before the operation.
        reset_modules (bool)[True]: If True reset sys.modules back to the original sys.modules.
    """
    modules = {k: v for k, v in sys.modules.items()}
    paths = [p for p in sys.path]
    path_cache = {k: v for k, v in sys.path_importer_cache.items()}

    # Temporarily add the new path
    if new_path and new_path not in sys.path:
        sys.path.insert(0, new_path)

    # # Clean modules (This causes breaking)
    # if clean_modules and not isinstance(clean_modules, (list, tuple)):
    #     clean_modules = list(sys.modules.keys())
    # if isinstance(clean_modules, (list, tuple)):
    #     # sys.path_importer_cache = {}  # Do I need this?
    #     # Clear only the given modules
    #     for pkg in clean_modules:
    #         try:
    #             if pkg not in sys.builtin_module_names:  # Cannot remove and reimport builtins properly
    #                 mod = sys.modules.pop(pkg)
    #                 del mod
    #         except (AttributeError, KeyError, Exception):
    #             pass

    yield

    if reset_modules:
        # sys.modules = modules  # For some reason this causes conflicts with relative imports?
        sys.modules.clear()
        sys.modules.update(modules)

    # Reset paths
    sys.path.clear()
    sys.path.extend(paths)

    sys.path_importer_cache = path_cache


def import_module(path, import_chain=None, reset_modules=True, dependent_modules=None, import_hook=None, **kwargs):
    """Import the given module name from the given import path.

    Args:
        path (str): Directory which contains the module to import.
        import_chain (str): Chain to import with.
        reset_modules (bool)[True]: If True reset sys.modules back to the original sys.modules.
        dependent_modules (dict)[None]: If a dict is given save all imported modules to this dictionary.
        import_hook (SaveImportHook)[DefaultHook]: Import hook to save imports.

    Returns:
        module (ModuleType): Module object that was imported.

    Raises:
        ImportError: If the import is unsuccessful.
    """
    if import_hook is None:
        import_hook = DefaultHook

    directory = path
    if import_chain is None:
        import_chain, directory = get_import_chain(path)

    if os.path.isfile(directory):
        directory = os.path.dirname(directory)

    if os.path.exists(directory):
        # Import the module
        with original_system(os.path.abspath(directory), reset_modules=reset_modules, **kwargs):
            with import_hook:
                # module = importlib.import_module(import_chain)
                module = __import__(import_chain, fromlist=(import_chain,))  # Works much better

            try:
                if isinstance(dependent_modules, dict):
                    dependent_modules.update(import_hook.get_modules())
            except (AttributeError, Exception):
                pass

        return module


def get_import_chain(path):
    """Find and return the import chain (package.module.submodule) for the given path."""
    path = os.path.splitext(os.path.abspath(path))[0]
    names = [os.path.basename(path)]
    path = os.path.dirname(path)

    while os.path.exists(os.path.join(path, '__init__.py')):
        names.append(os.path.basename(path))
        path = os.path.dirname(path)

    import_chain = '.'.join(reversed(names))
    return import_chain, path
