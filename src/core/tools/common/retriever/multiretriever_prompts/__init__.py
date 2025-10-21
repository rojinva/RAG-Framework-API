import importlib
import pkgutil

def import_submodules(package_name):
    package = importlib.import_module(package_name)
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        full_module_name = f"{package_name}.{module_name}"
        importlib.import_module(full_module_name)
        if is_pkg:
            import_submodules(full_module_name)

# Dynamically import all submodules
import_submodules(__name__)