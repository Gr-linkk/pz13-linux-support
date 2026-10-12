#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regression checks for native-detail focus scoring and verified selection."""
import importlib.util
from pathlib import Path
import unittest

import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf, GLib

spec = importlib.util.spec_from_file_location('focus', Path(__file__).resolve().parents[1] / 'camera/app/score-pz13-camera-focus.py')
focus = importlib.util.module_from_spec(spec)
spec.loader.exec_module(focus)


def target(outside=90, detailed=True):
    width, height = 1280, 960
    data = bytearray(width*height*3)
    for y in range(height):
        for x in range(width):
            center = 320 <= x < 960 and 240 <= y < 720
            value = (220 if (x//3 + y//11) % 2 else 30) if center and detailed else (90 if center else outside)
            offset = (y*width+x)*3
            data[offset:offset+3] = bytes((value, value, value))
    return GdkPixbuf.Pixbuf.new_from_bytes(GLib.Bytes.new(bytes(data)), GdkPixbuf.Colorspace.RGB,
                                         False, 8, width, height, width*3)


class FocusTests(unittest.TestCase):
    def test_native_detail_prefers_sharp_center(self):
        sharp = target()
        blurred = sharp.scale_simple(320, 240, GdkPixbuf.InterpType.BILINEAR).scale_simple(
            1280, 960, GdkPixbuf.InterpType.BILINEAR)
        self.assertGreater(focus.score_focus_pixbuf(sharp)['score'],
                           focus.score_focus_pixbuf(blurred)['score']*2)

    def test_peripheral_brightness_does_not_set_focus(self):
        dim = focus.score_focus_pixbuf(target(outside=30))
        bright = focus.score_focus_pixbuf(target(outside=230))
        self.assertAlmostEqual(dim['score'], bright['score'])
        self.assertGreater(bright['scene_luma'], dim['scene_luma'])

    def test_flat_subject_has_no_focus_detail(self):
        self.assertEqual(focus.score_focus_pixbuf(target(detailed=False))['score'], 0)

    def test_choice_must_remain_sharp(self):
        values = [{'controls_before': 'fixed', 'controls_after': 'fixed', 'luma': 120, 'scene_luma': 100}]
        self.assertTrue(focus.verified_focus(values, 1, 1.05, 1.04))
        for coarse, chosen, returned in ((1, .6, .6), (1, 1, .7), (1, 1, 1.4), (0, 0, 0)):
            with self.subTest(scores=(coarse, chosen, returned)):
                self.assertFalse(focus.verified_focus(values, coarse, chosen, returned))
        for change in ({'luma': 10}, {'controls_after': 'changed'}):
            self.assertFalse(focus.verified_focus([dict(values[0], **change)], 1, 1, 1))
        self.assertFalse(focus.verified_focus(values+[dict(values[0], scene_luma=120)], 1, 1, 1))
        self.assertFalse(focus.stable_measurements([]))


if __name__ == '__main__':
    unittest.main()
