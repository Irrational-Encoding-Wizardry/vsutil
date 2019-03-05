A collection of general-purpose Vapoursynth functions to be reused in modules and scripts.

## Functions
For more detail please check out the docstrings in the Python script.
* *get_subsampling*(clip):<br>
    Returns the subsampling of a given clip

* *get_depth*(clip):<br>
    Returns the bitdepth of a given clip

* *iterate*(base, function, count):<br>
	Executes a given function for the given amount of times

* *insert_clip*(clip, insert, start_frame):<br>
    Inserts a given clip into another one<br>
        The inserted clip cannot go beyond the final frame of the source clip

* *fallback*(value, fallback value):<br>
    Returns a value or the fallback value if the value is None

* *get_y*(clip):<br>
    Returns the luma of a given clip

* *split*(clip)<br>
    Returns a list of planes for the given clip

* *join*(planes, family): (Default: family=YUV)<br>
    Joins the supplied list of planes