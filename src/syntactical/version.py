from importlib.metadata import version, PackageNotFoundError

try:
    # Find the version of Syntactical and put it in the __version__ variable that can be externally imported from the main file:
    __version__ = version("syntactical")

# If Syntactical is not found (this should never happen; you are using Syntactical) then just put "unknown" as the version:
except PackageNotFoundError:
    __version__ = "unknown"
