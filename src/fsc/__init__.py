"""fsc package"""

try:
  from ._version import version as __version__
except ImportError:
  __version__ = "0.0.0"

from . import main

__all__ = ["main"]
