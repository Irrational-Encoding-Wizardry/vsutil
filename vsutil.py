"""
VSUtil. A collection of general-purpose VapourSynth functions to be reused in modules and scripts.
"""
__all__ = ['Dither', 'Range', 'core', 'depth', 'fallback', 'frame2clip', 'get_depth', 'get_plane_size',
           'get_subsampling', 'get_w', 'get_y', 'insert_clip', 'is_image', 'iterate', 'join', 'plane', 'split', 'vs']

from enum import Enum, EnumMeta, IntEnum
from functools import reduce
from mimetypes import types_map
from os import path
from typing import Callable, List, Literal, Optional, Tuple, TypeVar, Union

import vapoursynth as vs

core = vs.core
T = TypeVar('T')


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


def iterate(base: T, function: Callable[[T], T], count: int) -> T:
    """
    Utility function that executes a given function a given number of times.
    """
    return reduce(lambda v, _: function(v), range(count), base)


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


def get_y(clip: vs.VideoNode, /) -> vs.VideoNode:
    """
    Helper to get the luma of a VideoNode.

    If passed a single-plane vs.GRAY clip, it is assumed to be the luma and returned (no-op).
    """
    if clip.format is None or clip.format.color_family not in (vs.YUV, vs.YCOCG, vs.GRAY):
        raise ValueError('The clip must have a luma plane.')
    return plane(clip, 0)


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
        range input. Defaults to 'none', or round to nearest, otherwise.

    :return: Converted clip with desired bit depth and sample type. ColorFamily will be same as input.
    """

    if sample_type is not None:
        try:
            sample_type = vs.SampleType(sample_type)
        except ValueError:
            raise ValueError(f'depth: sample_type must be in {_readable_enums(vs.SampleType, str(vs.__name__))}.') from None
    if range is not None:
        try:
            range = Range(range)
        except ValueError:
            raise ValueError(f'depth: range must be in {_readable_enums(Range)}.') from None
    if range_in is not None:
        try:
            range_in = Range(range_in)
        except ValueError:
            raise ValueError(f'depth: range_in must be in {_readable_enums(Range)}.') from None
    if dither_type is not None:
        try:
            dither_type = Dither(dither_type)
        except ValueError:
            raise ValueError(f'depth: dither_type must be in {_readable_enums(Dither)}.') from None

    curr_depth = get_depth(clip)
    sample_type = fallback(sample_type, vs.FLOAT if bitdepth == 32 else vs.INTEGER)

    if (curr_depth, clip.format.sample_type, range_in) == (bitdepth, sample_type, range):
        return clip

    # thanks @Frechdachs for explaining this:
    # 'you need dithering when raising the bitdepth of full range [or] converting between full and limited'
    should_dither = (range_in != range
                     or range_in == Range.FULL
                     or (curr_depth > bitdepth and sample_type == vs.INTEGER))
    dither_type = fallback(dither_type, Dither.ERROR_DIFFUSION if should_dither else Dither.NONE)

    return clip.resize.Point(format=clip.format.replace(bits_per_sample=bitdepth, sample_type=sample_type), range=range,
                             range_in=range_in, dither_type=dither_type.value)


def _readable_enums(enum: EnumMeta, module: str = 'vsutil') -> list:
    """
    Returns a list of all possible values in `module.enum`.
    Extends the default `repr(enum.value)` behavior by prefixing the enum with the name of the module it belongs to.
    """
    return [f'<{module}.{str(e)}: {e.value}>' for e in enum]
