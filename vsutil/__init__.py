"""
VSUtil. A collection of general-purpose VapourSynth functions to be reused in modules and scripts.
"""
__all__ = ['Dither', 'Range', 'depth', 'disallow_variable_format', 'disallow_variable_resolution', 'fallback',
           'frame2clip', 'get_depth', 'get_plane_size',
           'get_subsampling', 'get_w', 'get_y', 'insert_clip', 'is_image', 'iterate', 'join', 'plane',
           'split']

from enum import Enum, IntEnum
from functools import wraps
from mimetypes import types_map
from os import path
from typing import Any, Callable, cast, List, Literal, Optional, Tuple, Type, TypeVar, Union

import vapoursynth as vs
core = vs.core

T = TypeVar('T')
E = TypeVar('E', bound=Enum)
R = TypeVar('R')
F = TypeVar('F', bound=Callable[..., Any])


class Range(IntEnum):
    """
    enum for zimg_pixel_range_e
    """
    LIMITED = 0  # Studio (TV) legal range, 16-235 in 8 bits.
    FULL =    1  # Full (PC) dynamic range, 0-255 in 8 bits.


class Dither(Enum):
    """
    enum for zimg_dither_type_e
    """
    NONE =            'none'             # Round to nearest.
    ORDERED =         'ordered'          # Bayer patterned dither.
    RANDOM =          'random'           # Pseudo-random noise of magnitude 0.5.
    ERROR_DIFFUSION = 'error_diffusion'  # Floyd-Steinberg error diffusion.


def disallow_variable_format(function: F) -> F:
    """
    Function decorator that raises an exception if the input clip has a variable format.
    Decorated function's first parameter must be of type `vapoursynth.VideoNode` and is the only parameter checked.
    """
    @wraps(function)
    def _check(clip: vs.VideoNode, *args, **kwargs) -> Any:
        if clip.format is None:
            raise ValueError('Variable-format clips not supported.')
        return function(clip, *args, **kwargs)
    return cast(F, _check)


def disallow_variable_resolution(function: F) -> F:
    """
    Function decorator that raises an exception if the input clip has a variable resolution.
    Decorated function's first parameter must be of type `vapoursynth.VideoNode` and is the only parameter checked.
    """
    @wraps(function)
    def _check(clip: vs.VideoNode, *args, **kwargs) -> Any:
        if 0 in (clip.width, clip.height):
            raise ValueError('Variable-resolution clips not supported.')
        return function(clip, *args, **kwargs)
    return cast(F, _check)


@disallow_variable_format
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


@disallow_variable_format
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


def iterate(base: T, function: Callable[[Union[T, R]], R], count: int) -> Union[T, R]:
    """
    Utility function that executes a given function a given number of times.
    """
    if count < 0:
        raise ValueError('Count cannot be negative.')

    v: Union[T, R] = base
    for _ in range(count):
        v = function(v)
    return v


def insert_clip(clip: vs.VideoNode, /, insert: vs.VideoNode, start_frame: int) -> vs.VideoNode:
    """
    Convenience method to insert a shorter clip into a longer one.
    The inserted clip cannot go beyond the last frame of the source clip or an exception is raised.
    """
    if start_frame == 0:
        return insert + clip[insert.num_frames:]
    pre = clip[:start_frame]
    frame_after_insert = start_frame + insert.num_frames
    if frame_after_insert > clip.num_frames:
        raise ValueError('Inserted clip is too long.')
    if frame_after_insert == clip.num_frames:
        return pre + insert
    post = clip[start_frame + insert.num_frames:]
    return pre + insert + post


def fallback(value: Optional[T], fallback_value: T) -> T:
    """
    Utility function that returns a value or a fallback if the value is None.
    """
    return fallback_value if value is None else value


@disallow_variable_format
def plane(clip: vs.VideoNode, planeno: int, /) -> vs.VideoNode:
    """
    Extract the plane with the given index from the clip.

    :param clip:     The clip to extract the plane from.
    :param planeno:  The index that specifies which plane to extract.
    :return: A grayscale clip that only contains the given plane.
    """
    if clip.format.num_planes == 1 and planeno == 0:
        return clip
    return core.std.ShufflePlanes(clip, planeno, vs.GRAY)


@disallow_variable_format
def get_y(clip: vs.VideoNode, /) -> vs.VideoNode:
    """
    Helper to get the luma of a VideoNode.

    If passed a single-plane vs.GRAY clip, it is assumed to be the luma and returned (no-op).
    """
    if clip.format.color_family not in (vs.YUV, vs.YCOCG, vs.GRAY):
        raise ValueError('The clip must have a luma plane.')
    return plane(clip, 0)


@disallow_variable_format
def split(clip: vs.VideoNode, /) -> List[vs.VideoNode]:
    """
    Returns a list of planes for the given input clip.
    """
    return [plane(clip, x) for x in range(clip.format.num_planes)]


def join(planes: List[vs.VideoNode],
         family: Literal[vs.ColorFamily.RGB, vs.ColorFamily.YUV, vs.ColorFamily.YCOCG] = vs.YUV) -> vs.VideoNode:
    """
    Joins the supplied list of planes into a three-plane VideoNode (defaults to YUV).
    """
    return core.std.ShufflePlanes(clips=planes, planes=[0, 0, 0], colorfamily=family)


def frame2clip(frame: vs.VideoFrame, /, *, enforce_cache=True) -> vs.VideoNode:
    """
    Converts a VapourSynth frame to a clip.

    :param frame:         The frame to wrap.
    :param enforce_cache: Always add a cache. (Even if the vapoursynth module has this feature disabled)
    :return: A one-frame VideoNode that yields the frame passed to the function.
    """
    bc = core.std.BlankClip(
        width=frame.width,
        height=frame.height,
        length=1,
        fpsnum=1,
        fpsden=1,
        format=frame.format.id
    )
    frame = frame.copy()
    result = bc.std.ModifyFrame([bc], lambda n, f: frame.copy())

    # Forcefully add a cache to Modify-Frame if caching is disabled on the core.
    # This will ensure that the filter will not include GIL characteristics.
    if not core.add_cache and enforce_cache:
        result = result.std.Cache(size=1, fixed=True)
    return result


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


@disallow_variable_format
def depth(clip: vs.VideoNode,
          bitdepth: int,
          /,
          sample_type: Optional[Union[int, vs.SampleType]] = None,
          *,
          range: Optional[Union[int, Range]] = None,
          range_in: Optional[Union[int, Range]] = None,
          dither_type: Optional[Union[Dither, str]] = None) \
        -> vs.VideoNode:
    """
    A bit depth converter only using core.resize and Format.replace.
    By default, outputs FLOAT sample type for 32 bit and INTEGER for anything else.

    :param bitdepth:    Desired bits_per_sample of output clip.
    :param sample_type: Desired sample_type of output clip. Allows overriding default FLOAT/INTEGER behavior. Accepts
                        vapoursynth.SampleType enums INTEGER and FLOAT or their values, [0, 1].
    :param range:       Output pixel range (defaults to input clip's range). See `Range`.
    :param range_in:    Input pixel range (defaults to input clip's range). See `Range`.
    :param dither_type: Dithering algorithm. Allows overriding default dithering behavior. See `Dither`.
        Defaults to Floyd-Steinberg error diffusion when downsampling, converting between ranges, or upsampling full
        range input. Defaults to 'none', or round to nearest, otherwise. See `_should_dither()` for more information.

    :return: Converted clip with desired bit depth and sample type. ColorFamily will be same as input.
    """
    sample_type = _resolve_enum(vs.SampleType, sample_type, 'sample_type', 'vapoursynth')
    range = _resolve_enum(Range, range, 'range')
    range_in = _resolve_enum(Range, range_in, 'range_in')
    dither_type = _resolve_enum(Dither, dither_type, 'dither_type')

    curr_depth = get_depth(clip)
    sample_type = fallback(sample_type, vs.FLOAT if bitdepth == 32 else vs.INTEGER)

    if (curr_depth, clip.format.sample_type, range_in) == (bitdepth, sample_type, range):
        return clip

    should_dither = _should_dither(curr_depth, bitdepth, range_in, range, clip.format.sample_type, sample_type)

    dither_type = fallback(dither_type, Dither.ERROR_DIFFUSION if should_dither else Dither.NONE)

    return clip.resize.Point(format=clip.format.replace(bits_per_sample=bitdepth, sample_type=sample_type),
                             range=range,
                             range_in=range_in,
                             dither_type=dither_type.value)


def _readable_enums(enum: Type[Enum], module: Optional[str] = None) -> str:
    """
    Returns a list of all possible values in `module.enum`.
    Extends the default `repr(enum.value)` behavior by prefixing the enum with the name of the module it belongs to.
    """
    return ', '.join([f'<{fallback(module, enum.__module__)}.{str(e)}: {e.value}>' for e in enum])


def _resolve_enum(enum: Type[E], value: Any, var_name: str, module: Optional[str] = None) -> Union[E, None]:
    """
    Attempts to evaluate `value` in `enum` if value is not None, otherwise returns None.
    Basically checks if a supplied enum value is valid and returns a readable error message
    explaining the possible enum values if it isn't.
    """
    if value is None:
        return None
    try:
        return enum(value)
    except ValueError:
        raise ValueError(f'{var_name} must be in {_readable_enums(enum, module)}.') from None


def _should_dither(in_bits: int,
                   out_bits: int,
                   in_range: Optional[Range] = None,
                   out_range: Optional[Range] = None,
                   in_sample_type: Optional[vs.SampleType] = None,
                   out_sample_type: Optional[vs.SampleType] = None,
                   ) -> bool:
    """
    Determines whether dithering is needed for a given depth/range/sample_type conversion.

    If an input range is specified, and output range *should* be specified otherwise it assumes a range conversion.

    For an explanation of when dithering is needed:
        - Dithering is NEVER needed if the conversion results in a float sample type.
        - Dithering is ALWAYS needed for a range conversion (i.e. full to limited or vice-versa).
        - Dithering is ALWAYS needed to convert a float sample type to an integer sample type.
        - Dithering is needed when upsampling full range content with the exception of 8 -> 16 bit upsampling,
          as this is simply (0-255) * 257 -> (0-65535).
        - Dithering is needed when downsampling limited or full range.

    Dithering is theoretically needed when converting from an integer depth greater than 10 to half float,
    despite the higher bit depth, but zimg's internal resampler currently does not dither for float output.
    """
    out_sample_type = fallback(out_sample_type, vs.FLOAT if out_bits == 32 else vs.INTEGER)
    in_sample_type = fallback(in_sample_type, vs.FLOAT if in_bits == 32 else vs.INTEGER)

    if out_sample_type == vs.FLOAT:
        return False

    range_conversion = in_range != out_range
    float_to_int = in_sample_type == vs.FLOAT
    upsampling = in_bits < out_bits
    downsampling = in_bits > out_bits

    return bool(range_conversion
                or float_to_int
                or (in_range == Range.FULL and upsampling and (in_bits, out_bits) != (8, 16))
                or downsampling)
