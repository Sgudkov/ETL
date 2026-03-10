import importlib
import pkgutil
import pathlib


def import_all_submodules(package_path: str, package_name: str):
    """
    Рекурсивно импортирует все модули внутри указанного пакета.
    """

    package_dir = pathlib.Path(package_path)

    for module in pkgutil.walk_packages(path=[package_path], prefix=package_name + "."):
        importlib.import_module(module.name)
