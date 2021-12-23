import sys

# From:
# https://github.com/mawillcockson/eggord/blob/ea7e56ce173561a550a08b67a9dafdaec149ff17/eggord/__init__.py
if sys.version_info >= (3, 8):
    from importlib import metadata as package_metadata
else:
    import importlib_metadata as package_metadata

APP_NAME = __name__
metadata = package_metadata.metadata(APP_NAME)
__version__ = str(metadata["version"])
APP_AUTHOR = str(metadata["author"])
