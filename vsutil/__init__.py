"""
VSUtil. A collection of general-purpose VapourSynth functions to be reused in modules and scripts.
"""

# export all public function directly
from .clips import *
from .func import *
from .info import *
from .types import *

# for wildcard imports
_mods = ['clips', 'func', 'info', 'types']

__all__ = []
for _pkg in _mods:
    __all__ += __import__(__name__ + '.' + _pkg, fromlist=_mods).__all__
