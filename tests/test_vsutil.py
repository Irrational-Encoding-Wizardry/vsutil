import unittest
import vapoursynth as vs
import vsutil


class VsUtilTests(unittest.TestCase):
    YUV420P8_CLIP = vs.core.std.BlankClip(_format=vs.YUV420P8, width=160, height=120, color=[0, 128, 128], length=100)
    YUV420P10_CLIP = vs.core.std.BlankClip(_format=vs.YUV420P10, width=160, height=120, color=[0, 128, 128], length=100)
    YUV444P8_CLIP = vs.core.std.BlankClip(_format=vs.YUV444P8, width=160, height=120, color=[0, 128, 128], length=100)
    YUV422P8_CLIP = vs.core.std.BlankClip(_format=vs.YUV422P8, width=160, height=120, color=[0, 128, 128], length=100)
    YUV410P8_CLIP = vs.core.std.BlankClip(_format=vs.YUV410P8, width=160, height=120, color=[0, 128, 128], length=100)
    YUV411P8_CLIP = vs.core.std.BlankClip(_format=vs.YUV411P8, width=160, height=120, color=[0, 128, 128], length=100)
    YUV440P8_CLIP = vs.core.std.BlankClip(_format=vs.YUV440P8, width=160, height=120, color=[0, 128, 128], length=100)

    BLACK_SAMPLE_CLIP = vs.core.std.BlankClip(_format=vs.YUV420P8, width=160, height=120, color=[0, 128, 128], length=100)
    WHITE_SAMPLE_CLIP = vs.core.std.BlankClip(_format=vs.YUV420P8, width=160, height=120, color=[255, 128, 128], length=100)

    def assert_same_dimensions(self, clip_a: vs.VideoNode, clip_b: vs.VideoNode):
        """
        Assert that two clips have the same width and height.
        """
        self.assertEqual(clip_a.height, clip_b.height, 'Same height expected, was {clip_a.height} and {clip_b.height}')
        self.assertEqual(clip_a.width, clip_b.width, 'Same width expected, was {clip_a.width} and {clip_b.width}')

    def assert_same_format(self, clip_a: vs.VideoNode, clip_b: vs.VideoNode):
        """
        Assert that two clips have the same format (but not necessarily size).
        """
        self.assertEqual(clip_a.format.id, clip_b.format.id, 'Same format expected')

    def assert_same_bitdepth(self, clip_a: vs.VideoNode, clip_b: vs.VideoNode):
        """
        Assert that two clips have the same number of bits per sample.
        """
        self.assertEqual(clip_a.format.bits_per_sample, clip_b.format.bits_per_sample,
                         'Same depth expected, was {clip_a.format.bits_per_sample} and {clip_b.format.bits_per_sample}')

    def assert_same_length(self, clip_a: vs.VideoNode, clip_b: vs.VideoNode):
        self.assertEqual(len(clip_a), len(clip_b),
                         'Same number of frames expected, was {len(clip_a)} and {len(clip_b)}.')

    def assert_same_metadata(self, clip_a: vs.VideoNode, clip_b: vs.VideoNode):
        """
        Assert that two clips have the same height and width, format, depth, and length.
        """
        self.assert_same_format(clip_a, clip_b)
        self.assert_same_dimensions(clip_a, clip_b)
        self.assert_same_length(clip_a, clip_b)

    def assert_same_frame(self, clip_a: vs.VideoNode, clip_b: vs.VideoNode, frameno: int = 0):
        """
        Assert that two frames are identical. Only the first frame of the arguments is used.
        """
        diff = vs.core.std.PlaneStats(clip_a, clip_b)
        frame = diff.get_frame(frameno)
        self.assertEqual(frame.props.PlaneStatsDiff, 0)

    def test_subsampling(self):
        self.assertEqual('444', vsutil.get_subsampling(self.YUV444P8_CLIP))
        self.assertEqual('440', vsutil.get_subsampling(self.YUV440P8_CLIP))
        self.assertEqual('420', vsutil.get_subsampling(self.YUV420P8_CLIP))
        self.assertEqual('422', vsutil.get_subsampling(self.YUV422P8_CLIP))
        self.assertEqual('411', vsutil.get_subsampling(self.YUV411P8_CLIP))
        self.assertEqual('410', vsutil.get_subsampling(self.YUV410P8_CLIP))

    def test_depth(self):
        self.assertEqual(8, vsutil.get_depth(self.YUV420P8_CLIP))
        self.assertEqual(10, vsutil.get_depth(self.YUV420P10_CLIP))

    def test_plane_size(self):
        self.assertEqual((160, 120), vsutil.get_plane_size(self.YUV420P8_CLIP, 0))
        self.assertEqual((80, 60), vsutil.get_plane_size(self.YUV420P8_CLIP, 1))

    def test_insert_clip(self):
        inserted_middle = vsutil.insert_clip(self.BLACK_SAMPLE_CLIP, self.WHITE_SAMPLE_CLIP[:10], 50)
        self.assert_same_frame(inserted_middle[0], self.BLACK_SAMPLE_CLIP[0])
        self.assert_same_frame(inserted_middle[50], self.WHITE_SAMPLE_CLIP[0])
        self.assert_same_frame(inserted_middle[60], self.BLACK_SAMPLE_CLIP[60])

        inserted_start = vsutil.insert_clip(self.BLACK_SAMPLE_CLIP, self.WHITE_SAMPLE_CLIP[:10], 0)
        self.assert_same_frame(inserted_start[0], self.WHITE_SAMPLE_CLIP[0])
        self.assert_same_frame(inserted_start[10], self.BLACK_SAMPLE_CLIP[10])

        inserted_end = vsutil.insert_clip(self.BLACK_SAMPLE_CLIP, self.WHITE_SAMPLE_CLIP[:10], 90)
        self.assert_same_frame(inserted_end[-1], self.WHITE_SAMPLE_CLIP[9])
        self.assert_same_frame(inserted_end[89], self.BLACK_SAMPLE_CLIP[89])

        # make sure we didn’t lose or add any frames in the process
        self.assert_same_metadata(self.BLACK_SAMPLE_CLIP, inserted_start)
        self.assert_same_metadata(self.BLACK_SAMPLE_CLIP, inserted_middle)
        self.assert_same_metadata(self.BLACK_SAMPLE_CLIP, inserted_end)

    def test_fallback(self):
        self.assertEqual(vsutil.fallback(None, 'a value'), 'a value')
        self.assertEqual(vsutil.fallback('a value', 'another value'), 'a value')
        self.assertEqual(vsutil.fallback(None, sum(range(5))), 10)

    def test_get_y(self):
        y = vsutil.get_y(self.BLACK_SAMPLE_CLIP)
        self.assertEqual(y.format.num_planes, 1)
        self.assert_same_dimensions(self.BLACK_SAMPLE_CLIP, y)
        self.assert_same_bitdepth(self.BLACK_SAMPLE_CLIP, y)

    def test_split_join(self):
        planes = vsutil.split(self.BLACK_SAMPLE_CLIP)
        self.assertEqual(len(planes), 3)
        self.assert_same_metadata(self.BLACK_SAMPLE_CLIP, vsutil.join(planes))

    def test_frame2clip(self):
        frame = self.WHITE_SAMPLE_CLIP.get_frame(0)
        clip = vsutil.frame2clip(frame)
        self.assert_same_frame(self.WHITE_SAMPLE_CLIP, clip)
