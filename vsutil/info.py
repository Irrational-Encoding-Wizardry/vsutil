"""
_
"""
__all__ = ['get_depth', 'get_plane_size', 'get_subsampling', 'get_w', 'is_image', 'scale_value']

from mimetypes import types_map
from os import path
from typing import Optional, Tuple, TypeVar, Union

import vapoursynth as vs

from . import func, types

core = vs.core

R = TypeVar('R')
T = TypeVar('T')


@func.disallow_variable_format
def get_depth(clip: vs.VideoNode, /) -> int:
    """
    Returns the bit depth of a VideoNode as an integer.
    """
    return clip.format.bits_per_sample


def get_plane_size(frame: Union[vs.VideoFrame, vs.VideoNode], /, planeno: int) -> Tuple[int, int]:
    """
    Calculates the dimensions (w, h) of the desired plane.

    :param frame:    Can be a clip or frame.
    :param planeno:  The desired plane's index.
    :return: (width, height)
    """
    # Add additional checks on VideoNodes as their size and format can be variable.
    if isinstance(frame, vs.VideoNode):
        if frame.width == 0:
            raise ValueError('Cannot calculate plane size of variable size clip. Pass a frame instead.')
        if frame.format is None:
            raise ValueError('Cannot calculate plane size of variable format clip. Pass a frame instead.')

    width, height = frame.width, frame.height
    if planeno != 0:
        width >>= frame.format.subsampling_w
        height >>= frame.format.subsampling_h
    return width, height


@func.disallow_variable_format
def get_subsampling(clip: vs.VideoNode, /) -> Union[None, str]:
    """
    Returns the subsampling of a VideoNode in human-readable format.
    Returns None for formats without subsampling.
    """
    if clip.format.color_family not in (vs.YUV, vs.YCOCG):
        return None
    if clip.format.subsampling_w == 1 and clip.format.subsampling_h == 1:
        return '420'
    elif clip.format.subsampling_w == 1 and clip.format.subsampling_h == 0:
        return '422'
    elif clip.format.subsampling_w == 0 and clip.format.subsampling_h == 0:
        return '444'
    elif clip.format.subsampling_w == 2 and clip.format.subsampling_h == 2:
        return '410'
    elif clip.format.subsampling_w == 2 and clip.format.subsampling_h == 0:
        return '411'
    elif clip.format.subsampling_w == 0 and clip.format.subsampling_h == 1:
        return '440'
    else:
        raise ValueError('Unknown subsampling.')


def get_w(height: int, aspect_ratio: float = 16 / 9, *, only_even: bool = True) -> int:
    """
    Calculates the width for a clip with the given height and aspect ratio.
    only_even is True by default because it imitates the math behind most standard resolutions (e.g. 854x480).
    """
    width = height * aspect_ratio
    if only_even:
        return round(width / 2) * 2
    return round(width)


def is_image(filename: str, /) -> bool:
    """
    Returns true if a filename refers to an image.
    """
    return types_map.get(path.splitext(filename)[-1], '').startswith('image/')


def scale_value(value: Union[int, float],
                input_depth: int,
                output_depth: int,
                range_in: Union[int, types.Range] = 0,
                range: Optional[Union[int, types.Range]] = None,
                scale_offsets: bool = False,
                chroma: bool = False,
                ) -> Union[int, float]:
    """
    Scales a given value between bit depths, sample types, and/or ranges.
    :value:         Numeric value to be scaled
    :input_depth:   Bit depth of the "value" parameter. Use 32 for float samples
    :output_depth:  Bit depth to scale the input value to
    :range_in:      Pixel range of the input value. No clamping is performed
    :range:         Pixel range of the output value. No clamping is performed
    :scale_offsets: Whether or not to apply YUV offsets to float chroma and/or TV range integer values
                    e.g. when scaling a TV range value of 16 to float, setting this to True will return "0.0" rather
                    than "0.073059.."
    :chroma:        Whether to treat values as chroma instead of luma
    """
    range_in = types._resolve_enum(types.Range, range_in, 'range_in')
    range = types._resolve_enum(types.Range, range, 'range')
    range = func.fallback(range, range_in)

    if input_depth == 32:
        range_in = 1

    if output_depth == 32:
        range = 1

    def peak_pixel_value(bits: int, range_: Union[int, types.Range], chroma_: bool) -> int:
        """
        _
        """
        if bits == 32:
            return 1
        if range_:
            return (1 << bits) - 1
        return (224 if chroma_ else 219) << (bits - 8)

    input_peak = peak_pixel_value(input_depth, range_in, chroma)

    output_peak = peak_pixel_value(output_depth, range, chroma)

    if input_depth == output_depth and range_in == range:
        return value

    if scale_offsets:
        if output_depth == 32 and chroma:
            value -= 128 << (input_depth - 8)
        elif range and not range_in:
            value -= 16 << (input_depth - 8)

    value *= output_peak / input_peak

    if scale_offsets:
        if input_depth == 32 and chroma:
            value += 128 << output_depth - 8
        elif range_in and not range:
            value += 16 << (output_depth - 8)

    return value
