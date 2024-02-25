import sys

__all__ = ["tomllib", "importlib_resources"]


if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources
else:
    import importlib_resources
