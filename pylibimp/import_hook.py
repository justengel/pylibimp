"""
Found that pydev uses this approach.
"""
import sys
import importlib
from types import ModuleType

if sys.version_info[0] >= 3:
    import builtins  # py3
else:
    import __builtin__ as builtins


__all__ = ['ImportHook', 'SaveImportHook', 'SaveBuiltinsImportHook', 'SaveImportlibImportHook',
           'ChainImportHooks', 'DefaultHook']


class ImportHook(ModuleType):
    """Import hook to modify imports that are imported after `setup()` is called."""
    SYSTEM_IMPORT = staticmethod(builtins.__import__)
    DEFAULT_NAME = __name__ + '.import_hook'

    def __init__(self, name=None, system_import=None, *args, **kwargs):
        if name is None:
            name = self.DEFAULT_NAME
        if system_import is None:
            system_import = self.SYSTEM_IMPORT

        ModuleType.__init__(self, name)

        self.system_import = system_import
        self.orig_import = None

    def do_import(self, *args, **kwargs):
        """import the given module name."""
        return self.system_import(*args, **kwargs)

    def setup(self):
        """Change imports to run this objects `do_import` method."""
        if builtins.__import__ == self.do_import:
            return self

        self.orig_import = builtins.__import__
        builtins.__import__ = self.do_import
        return self

    def teardown(self):
        """Stop running this objects `do_import` method and revert the import to the original import system."""
        try:
            if self.orig_import:
                builtins.__import__ = self.orig_import
        except (TypeError, ValueError, Exception):
            pass
        self.orig_import = None

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()
        return exc_type is None

    def __call__(self, *args, **kwargs):
        return self.do_import(*args, **kwargs)


class SaveImportHook(ImportHook):
    """Import hook that will save all of the modules that are imported after `setup()` is called."""
    def __init__(self, name=None, system_import=None, *args, **kwargs):
        super().__init__(name, system_import=system_import)
        self.modules = {}

    def get_modules(self):
        """Return a dict of modules that were imported."""
        return self.modules.copy()

    def save_module(self, name, module):
        """Save a module that was imported."""
        self.modules[name] = module

    def do_import(self, name, *args, **kwargs):
        """import the given module name."""
        module = self.system_import(name, *args, **kwargs)
        self.save_module(name, module)
        return module


class SaveBuiltinsImportHook(SaveImportHook):
    """Import hook that will save all of the modules that are imported after `setup()` is called."""
    SYSTEM_IMPORT = staticmethod(builtins.__import__)
    DEFAULT_NAME = __name__ + '.builtin_import_hook'

    def setup(self):
        """Change imports to run this objects `do_import` method."""
        if builtins.__import__ == self.do_import:
            return self

        self.orig_import = builtins.__import__
        builtins.__import__ = self.do_import
        return self

    def teardown(self):
        """Stop running this objects `do_import` method and revert the import to the original import system."""
        try:
            if self.orig_import:
                builtins.__import__ = self.orig_import
        except (TypeError, ValueError, Exception):
            pass
        self.orig_import = None


class SaveImportlibImportHook(SaveImportHook):
    SYSTEM_IMPORT = staticmethod(importlib.import_module)
    DEFAULT_NAME = __name__ + '.importlib_import_hook'

    def do_import(self, name, package=None, *args, **kwargs):
        """import the given module name."""
        module = self.system_import(name, package)

        import_chain = name
        if package is not None:
            if not import_chain.startswith('.'):
                import_chain = '.' + import_chain
            import_chain = package + import_chain
        self.save_module(import_chain, module)

        return module

    def setup(self):
        """Setup so imports are saved."""
        if importlib.import_module == self.do_import:
            return self

        self.orig_import = importlib.import_module
        importlib.import_module = self.do_import
        return self

    def teardown(self):
        """Stop saving imports and revert the imports to the original import system."""
        try:
            if self.orig_import:
                importlib.import_module = self.orig_import
        except (TypeError, ValueError, Exception):
            pass
        self.orig_import = None
        return self.get_modules()


class ChainImportHooks(SaveImportHook):
    def __init__(self, hooks=None, name=None, system_import=None, *args, **kwargs):
        super().__init__(name, system_import, *args, **kwargs)

        self.hooks = []

        try:
            self.hooks.extend(iter(hooks))
        except (AttributeError, TypeError, ValueError, Exception):
            try:
                if hooks is not None:
                    self.hooks.append(hooks)
            except (AttributeError, TypeError, ValueError, Exception):
                pass

    def get_modules(self):
        """Return a dict of modules that were imported."""
        d = self.modules.copy()
        for hook in self.hooks:
            try:
                d.update(hook.get_modules())
            except (AttributeError, Exception):
                pass
        return d

    def do_import(self, *args, **kwargs):
        """import the given module name."""
        for hook in self.hooks:
            try:
                return hook(*args, **kwargs)
            except (ImportError, AttributeError, TypeError, ValueError, Exception):
                pass

    def setup(self):
        """Change imports to run this objects `do_import` method."""
        for hook in self.hooks:
            try:
                hook.setup()
            except (ImportError, AttributeError, TypeError, ValueError, Exception):
                pass

    def teardown(self):
        """Stop running this objects `do_import` method and revert the import to the original import system."""
        for hook in self.hooks:
            try:
                hook.teardown()
            except (ImportError, AttributeError, TypeError, ValueError, Exception):
                pass


DefaultHook = ChainImportHooks([SaveBuiltinsImportHook(), SaveImportlibImportHook()])
