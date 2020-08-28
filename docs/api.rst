=============
API Reference
=============

.. automodule:: vsutil


Functions that return a clip
============================

.. autofunction:: vsutil.depth

    .. versionadded:: 0.3.0

.. autofunction:: vsutil.frame2clip

    .. versionchanged:: 0.2.0
        Added *enforce_cache* parameter.

.. autofunction:: vsutil.get_y
.. autofunction:: vsutil.insert_clip
.. autofunction:: vsutil.join
.. autofunction:: vsutil.plane
.. autofunction:: vsutil.split


Miscellanious non-VapourSynth functions
=======================================

.. autofunction:: vsutil.fallback
.. autofunction:: vsutil.iterate


Decorators
==========

.. autofunction:: vsutil.disallow_variable_format

    .. versionadded:: 0.4.0

.. autofunction:: vsutil.disallow_variable_resolution

    .. versionadded:: 0.4.0


Clip information and helper functions
=====================================

**Helpers to inspect a clip/frame**

.. autofunction:: vsutil.get_depth
.. autofunction:: vsutil.get_plane_size
.. autofunction:: vsutil.get_subsampling

    .. versionchanged:: 0.3.0
        Returns ``None`` for formats without subsampling (i.e. RGB).

.. autofunction:: vsutil.is_image

----

**Mathematical helpers**

.. autofunction:: vsutil.get_w
.. autofunction:: vsutil.scale_value

    .. versionadded:: 0.5.0


Enums
=====

.. autoclass:: vsutil.Dither
    :members:
.. autoclass:: vsutil.Range
    :members:
