"""
Decorators and non-VapourSynth-related functions.
"""
__all__ = [
    # decorators
    'disallow_variable_format', 'disallow_variable_resolution',
    # misc non-vapoursynth related
    'fallback', 'iterate',
]

import functools
from typing import Any, Callable, cast, Optional, TypeVar, Union

import vapoursynth as vs

F = TypeVar('F', bound=Callable)
T = TypeVar('T')
R = TypeVar('R')


def disallow_variable_format(function: F) -> F:
    """Function decorator that raises an exception if the input clip has a variable format.

    Decorated `function`'s first parameter must be of type ``vapoursynth.VideoNode`` and is the only parameter checked.
    """

    @functools.wraps(function)
    def _check(clip: vs.VideoNode, *args, **kwargs) -> Any:
        if clip.format is None:
            raise ValueError('Variable-format clips not supported.')
        return function(clip, *args, **kwargs)

    return cast(F, _check)


def disallow_variable_resolution(function: F) -> F:
    """Function decorator that raises an exception if the input clip has a variable resolution.

    Decorated `function`'s first parameter must be of type ``vapoursynth.VideoNode`` and is the only parameter checked.
    """

    @functools.wraps(function)
    def _check(clip: vs.VideoNode, *args, **kwargs) -> Any:
        if 0 in (clip.width, clip.height):
            raise ValueError('Variable-resolution clips not supported.')
        return function(clip, *args, **kwargs)

    return cast(F, _check)


def fallback(value: Optional[T], fallback_value: T) -> T:
    """Utility function that returns a value or a fallback if the value is ``None``.

    >>> fallback(5, 6)
    5
    >>> fallback(None, 6)
    6

    :param value:           Argument that can be ``None``.
    :param fallback_value:  Fallback value that is returned if `value` is ``None``.

    :return:                The input `value` or `fallback_value` if `value` is ``None``.
    """
    return fallback_value if value is None else value


def iterate(base: T, function: Callable[[Union[T, R]], R], count: int) -> Union[T, R]:
    """Utility function that executes a given function a given number of times.

    >>> def double(x):
    ...     return x * 2
    ...
    >>> iterate(5, double, 2)
    20

    :param base:      Initial value.
    :param function:  Function to execute.
    :param count:     Number of times to execute `function`.

    :return:          `function`'s output after repeating `count` number of times.
    """
    if count < 0:
        raise ValueError('Count cannot be negative.')

    v: Union[T, R] = base
    for _ in range(count):
        v = function(v)
    return v
