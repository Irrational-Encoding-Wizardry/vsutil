=============
API Reference
=============

.. automodule:: vsutil


Functions that return a clip
============================

.. autofunction:: vsutil.depth
.. autofunction:: vsutil.frame2clip
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
.. autofunction:: vsutil.disallow_variable_resolution


Clip information and helper functions
=====================================

**Helpers to inspect a clip/frame**

.. autofunction:: vsutil.get_depth
.. autofunction:: vsutil.get_plane_size
.. autofunction:: vsutil.get_subsampling
.. autofunction:: vsutil.is_image

----

**Mathematical helpers**

.. autofunction:: vsutil.get_w
.. autofunction:: vsutil.scale_value


Enums
=====

.. autoclass:: vsutil.Dither
    :members:
.. autoclass:: vsutil.Range
    :members:

Other
=====
.. py:data:: vsutil.EXPR_VARS
    :type: str
    :value: 'xyzabcdefghijklmnopqrstuvw'

    This constant contains a list of all variables that can appear inside an expr-string ordered
    by assignment. So the first clip will have the name *EXPR_VARS[0]*, the second one will
    have the name *EXPR_VARS[1]*, and so on.

    This can be used to automatically generate expr-strings.

