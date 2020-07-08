import unittest
import vapoursynth as vs
import vsutil


class VsUtilTests(unittest.TestCase):
    YUV420P8_CLIP = vs.core.std.BlankClip(format=vs.YUV420P8, width=160, height=120, color=[0, 128, 128], length=100)
    YUV420P10_CLIP = vs.core.std.BlankClip(format=vs.YUV420P10, width=160, height=120, color=[0, 128, 128], length=100)
    YUV444P8_CLIP = vs.core.std.BlankClip(format=vs.YUV444P8, width=160, height=120, color=[0, 128, 128], length=100)
    YUV422P8_CLIP = vs.core.std.BlankClip(format=vs.YUV422P8, width=160, height=120, color=[0, 128, 128], length=100)
    YUV410P8_CLIP = vs.core.std.BlankClip(format=vs.YUV410P8, width=160, height=120, color=[0, 128, 128], length=100)
    YUV411P8_CLIP = vs.core.std.BlankClip(format=vs.YUV411P8, width=160, height=120, color=[0, 128, 128], length=100)
    YUV440P8_CLIP = vs.core.std.BlankClip(format=vs.YUV440P8, width=160, height=120, color=[0, 128, 128], length=100)
    RGB24_CLIP = vs.core.std.BlankClip(format=vs.RGB24)

    SMALLER_SAMPLE_CLIP = vs.core.std.BlankClip(format=vs.YUV420P8, width=10, height=10)

    BLACK_SAMPLE_CLIP = vs.core.std.BlankClip(format=vs.YUV420P8, width=160, height=120, color=[0, 128, 128],
                                              length=100)
    WHITE_SAMPLE_CLIP = vs.core.std.BlankClip(format=vs.YUV420P8, width=160, height=120, color=[255, 128, 128],
                                              length=100)

    VARIABLE_FORMAT_CLIP = vs.core.std.Interleave([YUV420P8_CLIP, YUV444P8_CLIP], mismatch=True)

    def assert_same_dimensions(self, clip_a: vs.VideoNode, clip_b: vs.VideoNode):
        """
        Assert that two clips have the same width and height.
        """
        self.assertEqual(clip_a.height, clip_b.height, f'Same height expected, was {clip_a.height} and {clip_b.height}.')
        self.assertEqual(clip_a.width, clip_b.width, f'Same width expected, was {clip_a.width} and {clip_b.width}.')

    def assert_same_format(self, clip_a: vs.VideoNode, clip_b: vs.VideoNode):
        """
        Assert that two clips have the same format (but not necessarily size).
        """
        self.assertEqual(clip_a.format.id, clip_b.format.id, 'Same format expected.')

    def assert_same_bitdepth(self, clip_a: vs.VideoNode, clip_b: vs.VideoNode):
        """
        Assert that two clips have the same number of bits per sample.
        """
        self.assertEqual(clip_a.format.bits_per_sample, clip_b.format.bits_per_sample,
                         f'Same depth expected, was {clip_a.format.bits_per_sample} and {clip_b.format.bits_per_sample}.')

    def assert_same_length(self, clip_a: vs.VideoNode, clip_b: vs.VideoNode):
        self.assertEqual(len(clip_a), len(clip_b),
                         f'Same number of frames expected, was {len(clip_a)} and {len(clip_b)}.')

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
        self.assertEqual(None, vsutil.get_subsampling(self.RGB24_CLIP))
        # let’s create a custom format with higher subsampling than any of the legal ones to test that branch as well:
        with self.assertRaisesRegex(ValueError, 'Unknown subsampling.'):
            vsutil.get_subsampling(
                vs.core.std.BlankClip(_format=self.YUV444P8_CLIP.format.replace(subsampling_w=4))
            )

    def test_get_depth(self):
        self.assertEqual(8, vsutil.get_depth(self.YUV420P8_CLIP))
        self.assertEqual(10, vsutil.get_depth(self.YUV420P10_CLIP))

    def test_plane_size(self):
        self.assertEqual((160, 120), vsutil.get_plane_size(self.YUV420P8_CLIP, 0))
        self.assertEqual((80, 60), vsutil.get_plane_size(self.YUV420P8_CLIP, 1))
        # these should fail because they don’t have a constant format or size
        with self.assertRaises(ValueError):
            vsutil.get_plane_size(
                vs.core.std.Splice([self.BLACK_SAMPLE_CLIP, self.SMALLER_SAMPLE_CLIP], mismatch=True), 0)
        with self.assertRaises(ValueError):
            vsutil.get_plane_size(
                vs.core.std.Splice([self.YUV444P8_CLIP, self.YUV422P8_CLIP], mismatch=True), 0)

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

        with self.assertRaises(ValueError):
            vsutil.insert_clip(self.BLACK_SAMPLE_CLIP, self.BLACK_SAMPLE_CLIP, 90)

    def test_fallback(self):
        self.assertEqual(vsutil.fallback(None, 'a value'), 'a value')
        self.assertEqual(vsutil.fallback('a value', 'another value'), 'a value')
        self.assertEqual(vsutil.fallback(None, sum(range(5))), 10)

    def test_get_y(self):
        y = vsutil.get_y(self.BLACK_SAMPLE_CLIP)
        self.assertEqual(y.format.num_planes, 1)
        self.assert_same_dimensions(self.BLACK_SAMPLE_CLIP, y)
        self.assert_same_bitdepth(self.BLACK_SAMPLE_CLIP, y)

        with self.assertRaisesRegex(ValueError, 'The clip must have a luma plane.'):
            vsutil.get_y(self.RGB24_CLIP)

    def test_plane(self):
        y = vs.core.std.BlankClip(format=vs.GRAY8)
        # This should be a no-op, and even the clip reference shouldn’t change
        self.assertEqual(y, vsutil.plane(y, 0))

    def test_split_join(self):
        planes = vsutil.split(self.BLACK_SAMPLE_CLIP)
        self.assertEqual(len(planes), 3)
        self.assert_same_metadata(self.BLACK_SAMPLE_CLIP, vsutil.join(planes))

    def test_frame2clip(self):
        frame = self.WHITE_SAMPLE_CLIP.get_frame(0)
        clip = vsutil.frame2clip(frame)
        self.assert_same_frame(self.WHITE_SAMPLE_CLIP, clip)
        # specifically test the path with disabled cache
        try:
            vs.core.add_cache = False
            black_frame = self.BLACK_SAMPLE_CLIP.get_frame(0)
            black_clip = vsutil.frame2clip(black_frame)
            self.assert_same_frame(self.BLACK_SAMPLE_CLIP, black_clip)
        # reset state of the core for further tests
        finally:
            vs.core.add_cache = True

    def test_is_image(self):
        """These are basically tests for the mime types, but I want the coverage. rooDerp"""
        self.assertEqual(vsutil.is_image('something.png'), True)
        self.assertEqual(vsutil.is_image('something.m2ts'), False)

    def test_get_w(self):
        self.assertEqual(vsutil.get_w(480), 854)
        self.assertEqual(vsutil.get_w(480, only_even=False), 853)
        self.assertEqual(vsutil.get_w(1080, 4 / 3), 1440)
        self.assertEqual(vsutil.get_w(1080), 1920)

    def test_iterate(self):
        def double_number(x: int) -> int:
            return x * 2

        self.assertEqual(vsutil.iterate(2, double_number, 0), 2)
        self.assertEqual(vsutil.iterate(2, double_number, 1), double_number(2))
        self.assertEqual(vsutil.iterate(2, double_number, 3), double_number(double_number(double_number(2))))

        with self.assertRaisesRegex(ValueError, 'Count cannot be negative.'):
            vsutil.iterate(2, double_number, -1)

    def test_scale(self):
        # no change
        self.assertEqual(vsutil.scale(1, 8, 8, range_in=0, range=0), 1)
        self.assertEqual(vsutil.scale(1, 8, 8, range_in=1, range=1), 1)
        self.assertEqual(vsutil.scale(1, 32, 32, range_in=1, range=0), 1)
        self.assertEqual(vsutil.scale(1, 32, 32, range_in=0, range=1), 1)

        # range conversion
        self.assertEqual(vsutil.scale(219, 8, 8, range_in=0, range=1, scale_offsets=False, chroma=False), 255)
        self.assertEqual(vsutil.scale(255, 8, 8, range_in=1, range=0, scale_offsets=False, chroma=False), 219)

        self.assertEqual(vsutil.scale(224, 8, 8, range_in=0, range=1, scale_offsets=False, chroma=True), 255)
        self.assertEqual(vsutil.scale(255, 8, 8, range_in=1, range=0, scale_offsets=False, chroma=True), 224)

        self.assertEqual(vsutil.scale(235, 8, 8, range_in=0, range=1, scale_offsets=True, chroma=False), 255)
        self.assertEqual(vsutil.scale(255, 8, 8, range_in=1, range=0, scale_offsets=True, chroma=False), 235)

        self.assertEqual(vsutil.scale(240, 8, 8, range_in=0, range=1, scale_offsets=True, chroma=True), 255)
        self.assertEqual(vsutil.scale(255, 8, 8, range_in=1, range=0, scale_offsets=True, chroma=True), 240)

        # int to int (upsample)
        self.assertEqual(vsutil.scale(1, 8, 16, range_in=0, range=0, scale_offsets=False, chroma=False), 256)
        self.assertEqual(vsutil.scale(1, 8, 16, range_in=1, range=1, scale_offsets=False, chroma=False), 257)
        self.assertEqual(vsutil.scale(219, 8, 16, range_in=0, range=1, scale_offsets=False, chroma=False), 65535)
        self.assertEqual(vsutil.scale(255, 8, 16, range_in=1, range=0, scale_offsets=False, chroma=False), 219 << 8)

        self.assertEqual(vsutil.scale(1, 8, 16, range_in=0, range=0, scale_offsets=False, chroma=True), 256)
        self.assertEqual(vsutil.scale(1, 8, 16, range_in=1, range=1, scale_offsets=False, chroma=True), 257)
        self.assertEqual(vsutil.scale(224, 8, 16, range_in=0, range=1, scale_offsets=False, chroma=True), 65535)
        self.assertEqual(vsutil.scale(255, 8, 16, range_in=1, range=0, scale_offsets=False, chroma=True), 224 << 8)

        self.assertEqual(vsutil.scale(1, 8, 16, range_in=0, range=0, scale_offsets=True, chroma=False), 256)
        self.assertEqual(vsutil.scale(1, 8, 16, range_in=1, range=1, scale_offsets=True, chroma=False), 257)
        self.assertEqual(vsutil.scale(235, 8, 16, range_in=0, range=1, scale_offsets=True, chroma=False), 65535)
        self.assertEqual(vsutil.scale(255, 8, 16, range_in=1, range=0, scale_offsets=True, chroma=False), 235 << 8)

        self.assertEqual(vsutil.scale(1, 8, 16, range_in=0, range=0, scale_offsets=True, chroma=True), 256)
        self.assertEqual(vsutil.scale(1, 8, 16, range_in=1, range=1, scale_offsets=True, chroma=True), 257)
        self.assertEqual(vsutil.scale(240, 8, 16, range_in=0, range=1, scale_offsets=True, chroma=True), 65535)
        self.assertEqual(vsutil.scale(255, 8, 16, range_in=1, range=0, scale_offsets=True, chroma=True), 240 << 8)

        # int to flt
        self.assertEqual(vsutil.scale(1, 8, 32, range_in=0, range=1, scale_offsets=False, chroma=False), 1/219)
        self.assertEqual(vsutil.scale(1, 8, 32, range_in=1, range=1, scale_offsets=False, chroma=False), 1/255)
        self.assertEqual(vsutil.scale(219, 8, 32, range_in=0, range=1, scale_offsets=False, chroma=False), 1)
        self.assertEqual(vsutil.scale(255, 8, 32, range_in=1, range=1, scale_offsets=False, chroma=False), 1)

        self.assertEqual(vsutil.scale(1, 8, 32, range_in=0, range=1, scale_offsets=False, chroma=True), 1/224)
        self.assertEqual(vsutil.scale(1, 8, 32, range_in=1, range=1, scale_offsets=False, chroma=True), 1/255)
        self.assertEqual(vsutil.scale(224, 8, 32, range_in=0, range=1, scale_offsets=False, chroma=True), 1)
        self.assertEqual(vsutil.scale(255, 8, 32, range_in=1, range=1, scale_offsets=False, chroma=True), 1)

        self.assertEqual(vsutil.scale(1, 8, 32, range_in=0, range=1, scale_offsets=True, chroma=False), (1-16)/219)
        self.assertEqual(vsutil.scale(1, 8, 32, range_in=1, range=1, scale_offsets=True, chroma=False), 1/255)
        self.assertEqual(vsutil.scale(235, 8, 32, range_in=0, range=1, scale_offsets=True, chroma=False), 1)
        self.assertEqual(vsutil.scale(255, 8, 32, range_in=1, range=1, scale_offsets=True, chroma=False), 1)

        self.assertEqual(vsutil.scale(1, 8, 32, range_in=0, range=1, scale_offsets=True, chroma=True), (1-128)/224)
        self.assertEqual(vsutil.scale(1, 8, 32, range_in=1, range=1, scale_offsets=True, chroma=True), (1-128)/255)
        self.assertEqual(vsutil.scale(240, 8, 32, range_in=0, range=1, scale_offsets=True, chroma=True), 0.5)
        self.assertEqual(vsutil.scale(255, 8, 32, range_in=1, range=1, scale_offsets=True, chroma=True), (255-128)/255)

        # int to int (downsample)
        self.assertEqual(vsutil.scale(256, 16, 8, range_in=0, range=0, scale_offsets=False, chroma=False), 1)
        self.assertEqual(vsutil.scale(257, 16, 8, range_in=1, range=1, scale_offsets=False, chroma=False), 1)
        self.assertEqual(vsutil.scale(65535, 16, 8, range_in=1, range=0, scale_offsets=False, chroma=False), 219)
        self.assertEqual(vsutil.scale(219 << 8, 16, 8, range_in=0, range=1, scale_offsets=False, chroma=False), 255)

        self.assertEqual(vsutil.scale(256, 16, 8, range_in=0, range=0, scale_offsets=False, chroma=True), 1)
        self.assertEqual(vsutil.scale(257, 16, 8, range_in=1, range=1, scale_offsets=False, chroma=True), 1)
        self.assertEqual(vsutil.scale(65535, 16, 8, range_in=1, range=0, scale_offsets=False, chroma=True), 224)
        self.assertEqual(vsutil.scale(224<<8, 16, 8, range_in=0, range=1, scale_offsets=False, chroma=True), 255)

        self.assertEqual(vsutil.scale(256, 16, 8, range_in=0, range=0, scale_offsets=True, chroma=False), 1)
        self.assertEqual(vsutil.scale(257, 16, 8, range_in=1, range=1, scale_offsets=True, chroma=False), 1)
        self.assertEqual(vsutil.scale(65535, 16, 8, range_in=1, range=0, scale_offsets=True, chroma=False), 235)
        self.assertEqual(vsutil.scale(225<<8, 16, 8, range_in=0, range=1, scale_offsets=True, chroma=False), 255)

        self.assertEqual(vsutil.scale(256, 16, 8, range_in=0, range=0, scale_offsets=True, chroma=True), 1)
        self.assertEqual(vsutil.scale(257, 16, 8, range_in=1, range=1, scale_offsets=True, chroma=True), 1)
        self.assertEqual(vsutil.scale(65535, 16, 8, range_in=1, range=0, scale_offsets=True, chroma=True), 240)
        self.assertEqual(vsutil.scale(240<<8, 16, 8, range_in=0, range=1, scale_offsets=True, chroma=True), 255)

        # flt to int
        self.assertEqual(vsutil.scale(1/219, 32, 8, range_in=1, range=0, scale_offsets=False, chroma=False), 1)
        self.assertEqual(vsutil.scale(1/255, 32, 8, range_in=1, range=1, scale_offsets=False, chroma=False), 1)
        self.assertEqual(vsutil.scale(1, 32, 8, range_in=1, range=0, scale_offsets=False, chroma=False), 219)
        self.assertEqual(vsutil.scale(1, 32, 8, range_in=1, range=1, scale_offsets=False, chroma=False), 255)

        self.assertEqual(vsutil.scale(1/224, 32, 8, range_in=1, range=0, scale_offsets=False, chroma=True), 1)
        self.assertEqual(vsutil.scale(1/255, 32, 8, range_in=1, range=1, scale_offsets=False, chroma=True), 1)
        self.assertEqual(vsutil.scale(1, 32, 8, range_in=1, range=0, scale_offsets=False, chroma=True), 224)
        self.assertEqual(vsutil.scale(1, 32, 8, range_in=1, range=1, scale_offsets=False, chroma=True), 255)

        self.assertEqual(vsutil.scale((1-16)/219, 32, 8, range_in=1, range=0, scale_offsets=True, chroma=False), 1)
        self.assertEqual(vsutil.scale(1/255, 32, 8, range_in=1, range=1, scale_offsets=True, chroma=False), 1)
        self.assertEqual(vsutil.scale(1, 32, 8, range_in=1, range=0, scale_offsets=True, chroma=False), 235)
        self.assertEqual(vsutil.scale(1, 32, 8, range_in=1, range=1, scale_offsets=True, chroma=False), 255)

        self.assertEqual(vsutil.scale((1-128)/224, 32, 8, range_in=1, range=0, scale_offsets=True, chroma=True), 1)
        self.assertEqual(vsutil.scale((1-128)/255, 32, 8, range_in=1, range=1, scale_offsets=True, chroma=True), 1)
        self.assertEqual(vsutil.scale(0.5, 32, 8, range_in=1, range=0, scale_offsets=True, chroma=True), 240)
        self.assertEqual(vsutil.scale((255-128)/255, 32, 8, range_in=1, range=1, scale_offsets=True, chroma=True), 255)

    def test_depth(self):
        with self.assertRaisesRegex(ValueError, 'sample_type must be in'):
            vsutil.depth(self.RGB24_CLIP, 8, sample_type=2)
        with self.assertRaisesRegex(ValueError, 'range must be in'):
            vsutil.depth(self.RGB24_CLIP, 8, range=2)
        with self.assertRaisesRegex(ValueError, 'range_in must be in'):
            vsutil.depth(self.RGB24_CLIP, 8, range_in=2)
        with self.assertRaisesRegex(ValueError, 'dither_type must be in'):
            vsutil.depth(self.RGB24_CLIP, 8, dither_type='test')

        full_clip = vs.core.std.BlankClip(format=vs.RGB24)
        int_10_clip = full_clip.resize.Point(format=full_clip.format.replace(bits_per_sample=10))
        int_16_clip = full_clip.resize.Point(format=full_clip.format.replace(bits_per_sample=16))
        float_16_clip = full_clip.resize.Point(format=full_clip.format.replace(bits_per_sample=16, sample_type=vs.FLOAT))
        float_32_clip = full_clip.resize.Point(format=full_clip.format.replace(bits_per_sample=32, sample_type=vs.FLOAT))

        limited_clip = vs.core.std.BlankClip(format=vs.YUV420P8)
        l_int_10_clip = limited_clip.resize.Point(format=limited_clip.format.replace(bits_per_sample=10))
        l_int_16_clip = limited_clip.resize.Point(format=limited_clip.format.replace(bits_per_sample=16))
        l_float_16_clip = limited_clip.resize.Point(format=limited_clip.format.replace(bits_per_sample=16, sample_type=vs.FLOAT))
        l_float_32_clip = limited_clip.resize.Point(format=limited_clip.format.replace(bits_per_sample=32, sample_type=vs.FLOAT))

        self.assertEqual(vsutil.depth(full_clip, 8), full_clip)
        self.assert_same_format(vsutil.depth(full_clip, 10), int_10_clip)
        self.assert_same_format(vsutil.depth(full_clip, 16), int_16_clip)
        self.assert_same_format(vsutil.depth(full_clip, 16, sample_type=vs.FLOAT), float_16_clip)
        self.assert_same_format(vsutil.depth(full_clip, 32), float_32_clip)

        self.assert_same_format(vsutil.depth(float_16_clip, 16, sample_type=vs.INTEGER), int_16_clip)

        self.assertEqual(vsutil.depth(limited_clip, 8), limited_clip)
        self.assert_same_format(vsutil.depth(limited_clip, 10), l_int_10_clip)
        self.assert_same_format(vsutil.depth(limited_clip, 16), l_int_16_clip)
        self.assert_same_format(vsutil.depth(limited_clip, 16, sample_type=vs.FLOAT), l_float_16_clip)
        self.assert_same_format(vsutil.depth(limited_clip, 32), l_float_32_clip)

        self.assert_same_format(vsutil.depth(l_float_16_clip, 16, sample_type=vs.INTEGER), l_int_16_clip)

    def test_readable_enums(self):
        self.assertEqual(vsutil._readable_enums(vsutil.Range), '<vsutil.Range.LIMITED: 0>, <vsutil.Range.FULL: 1>')

    def test_resolve_enum(self):
        self.assertEqual(vsutil._resolve_enum(vsutil.Range, None, 'test'), None)
        self.assertEqual(vsutil._resolve_enum(vs.SampleType, 0, 'test', 'vapoursynth'), vs.SampleType(0))

        with self.assertRaisesRegex(ValueError, 'vapoursynth.ColorFamily'):
            vsutil._resolve_enum(vs.ColorFamily, 2, 'test', 'vapoursynth')

    def test_should_dither(self):
        # --- True ---
        # Range conversion
        self.assertTrue(vsutil._should_dither(1, 1, in_range=vsutil.Range.LIMITED, out_range=vsutil.Range.FULL))
        # Float to int
        self.assertTrue(vsutil._should_dither(1, 1, in_sample_type=vs.FLOAT))
        # Upsampling full range 10 -> 12
        self.assertTrue(vsutil._should_dither(10, 12, in_range=vsutil.Range.FULL, out_range=vsutil.Range.FULL))
        # Downsampling
        self.assertTrue(vsutil._should_dither(10, 8, in_sample_type=vs.INTEGER))
        self.assertTrue(vsutil._should_dither(10, 8, in_sample_type=vs.INTEGER, in_range=vsutil.Range.FULL, out_range=vsutil.Range.FULL))
        self.assertTrue(vsutil._should_dither(10, 8, in_sample_type=vs.INTEGER, in_range=vsutil.Range.LIMITED, out_range=vsutil.Range.LIMITED))

        # --- False ---
        # Int to int
        self.assertFalse(vsutil._should_dither(8, 8, in_sample_type=vs.INTEGER))
        # Upsampling full range 8 -> 16
        self.assertFalse(vsutil._should_dither(8, 16, in_range=vsutil.Range.FULL, out_range=vsutil.Range.FULL))
        # Upsampling
        self.assertFalse(vsutil._should_dither(8, 16, in_sample_type=vs.INTEGER))
        self.assertFalse(vsutil._should_dither(8, 16, in_sample_type=vs.INTEGER, in_range=vsutil.Range.LIMITED, out_range=vsutil.Range.LIMITED))
        # Float output
        self.assertFalse(vsutil._should_dither(32, 32, in_sample_type=vs.INTEGER))
        self.assertFalse(vsutil._should_dither(32, 16, in_sample_type=vs.INTEGER, out_sample_type=vs.FLOAT))

    def test_decorators(self):
        with self.assertRaisesRegex(ValueError, 'Variable-format'):
            vsutil.get_subsampling(self.VARIABLE_FORMAT_CLIP)
