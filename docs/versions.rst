===============
Version History
===============

.. automodule:: vsutil
   :noindex:

0.5.0
-----

..

- Split single ``__init__.py`` file into submodules.

- New functions:

  * :func:`scale_value` added to scale values for bit depth, sample type, or range conversion.

0.4.0
-----

..

- New functions:

  * :func:`disallow_variable_format` and :func:`disallow_variable_resolution` function decorators added that raise exceptions on variable-format or variable-res clips. Helpful for functions that assume the input clip's ``format`` is a valid ``vapoursynth.Format`` instance.

- Changes to existing functions:

  * Removed ``functools.reduce`` usage in :func:`iterate`, fixing type-hinting and disallowing negative ``count``.
  * Dithering logic in :func:`depth` is now handled in a separate private function.

- Bug fixes:

  * Will no longer dither for 8-bit full-range to 16-bit full-range conversions in :func:`depth`.

0.3.0
-----

..

- Now uses Python 3.8 positional-only arguments (see :pep:`570` for more information):

  * :func:`get_subsampling` ``clip`` parameter
  * :func:`get_depth` ``clip`` parameter
  * :func:`get_plane_size` ``frame`` parameter
  * :func:`insert_clip` ``clip`` parameter
  * :func:`plane` ``clip`` and ``planeno`` parameters
  * :func:`get_y` ``clip`` parameter
  * :func:`split` ``clip`` parameter
  * :func:`frame2clip` ``frame`` parameter
  * :func:`is_image` ``filename`` parameter

- New classes:

  * :class:`Dither` and :class:`Range` enumerations added to simpliy ``range``, ``range_in``, and ``dither_type`` arguments to ``vapoursynth.core.resize``.

- New functions:

  * Added a bit depth converter, :func:`depth`, that automatically handles dithering and format changes.

- Changes to existing functions:

  * :func:`get_subsampling` now returns ``None`` for formats without subsampling (i.e. RGB).
  * :func:`get_w` ``only_even`` parameter changed to keyword-only argument.

0.2.0
-----

..

- Changes to existing functions:

  * Added ``enforce_cache`` parameter to :func:`frame2clip`.

0.1.0
-----

- Initial package release.

- Included functions:

  * :func:`fallback`
  * :func:`frame2clip`
  * :func:`get_depth`
  * :func:`get_plane_size`
  * :func:`get_subsampling`
  * :func:`get_w`
  * :func:`get_y`
  * :func:`insert_clip`
  * :func:`is_image`
  * :func:`iterate`
  * :func:`join`
  * :func:`plane`
  * :func:`split`
