from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("syntactical")
except PackageNotFoundError:
    __version__ = "uninstalled" 
