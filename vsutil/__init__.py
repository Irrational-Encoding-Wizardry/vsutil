"""
VSUtil. A collection of general-purpose VapourSynth functions to be reused in modules and scripts.
"""

from vsutil.vsutil import Dither, Range
from vsutil.vsutil import depth, fallback, frame2clip
from vsutil.vsutil import get_depth, get_plane_size
from vsutil.vsutil import get_subsampling, get_w, get_y
from vsutil.vsutil import insert_clip, is_image, iterate
from vsutil.vsutil import join, plane, split

__all__ = ['Dither', 'Range', 'depth', 'fallback', 'frame2clip', 'get_depth', 'get_plane_size',
           'get_subsampling', 'get_w', 'get_y', 'insert_clip', 'is_image', 'iterate', 'join', 'plane', 'split']
