"""
Enums and related functions.
"""
__all__ = ['Dither', 'Range']

# this file only depends on the stdlib and should stay that way
from enum import Enum
from typing import Any, Optional, Type, TypeVar, Union

E = TypeVar('E', bound=Enum)


class Dither(str, Enum):
    """
    enum for zimg_dither_type_e
    """
    NONE =            'none'             # Round to nearest.
    ORDERED =         'ordered'          # Bayer patterned dither.
    RANDOM =          'random'           # Pseudo-random noise of magnitude 0.5.
    ERROR_DIFFUSION = 'error_diffusion'  # Floyd-Steinberg error diffusion.


class Range(int, Enum):
    """
    enum for zimg_pixel_range_e
    """
    LIMITED = 0  # Studio (TV) legal range, 16-235 in 8 bits.
    FULL =    1  # Full (PC) dynamic range, 0-255 in 8 bits.


def _readable_enums(enum: Type[Enum], module: Optional[str] = None) -> str:
    """
    Returns a list of all possible values in `module.enum`.
    Extends the default `repr(enum.value)` behavior by prefixing the enum with the name of the module it belongs to.
    """
    return ', '.join([f'<{module if module else enum.__module__}.{str(e)}: {e.value}>' for e in enum])


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
