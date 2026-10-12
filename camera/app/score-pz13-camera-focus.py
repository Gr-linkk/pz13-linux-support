#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Small read-only focus metric for the private rear-camera experiment.

Decode an existing JPEG with GdkPixbuf, downsample to suppress sensor noise,
then measure squared central-image gradients normalized by mean brightness.
This is a contrast metric, not an autofocus algorithm or optical calibration.
"""
import json
from pathlib import Path
import sys


def score_rows(rows):
    height, width = len(rows), len(rows[0])
    if height < 10 or width < 10 or any(len(row) != width for row in rows):
        raise ValueError('Rectangular luminance image required')
    # Separable [1, 2, 1] filtering preserves the original 3x3 metric while
    # avoiding nine Python generator iterations per pixel in the live search.
    horizontal = [[row[x-1] + 2*row[x] + row[x+1] for x in range(1, width-1)]
                  for row in rows]
    smoothed = [[(horizontal[y-1][x] + 2*horizontal[y][x] + horizontal[y+1][x])/16
                 for x in range(width-2)] for y in range(1, height-1)]
    y0, y1 = height//5, height*4//5-2
    x0, x1 = width//5, width*4//5-2
    mean = sum(smoothed[y][x] for y in range(y0, y1) for x in range(x0, x1)) / ((y1-y0)*(x1-x0))
    gradient = sum((smoothed[y][x+1]-smoothed[y][x-1])**2 +
                   (smoothed[y+1][x]-smoothed[y-1][x])**2
                   for y in range(y0, y1) for x in range(x0, x1)) / ((y1-y0)*(x1-x0))
    return {'score': gradient/max(mean*mean, 1.0), 'mean_luma': mean}


def pixbuf_rows(p):
    pixels, stride, channels = p.get_pixels(), p.get_rowstride(), p.get_n_channels()
    if channels not in (3, 4) or p.get_bits_per_sample() != 8:
        raise ValueError('Expected 8-bit RGB image')
    return [[(77*pixels[y*stride+x*channels] + 150*pixels[y*stride+x*channels+1] +
              29*pixels[y*stride+x*channels+2])/256
             for x in range(p.get_width())] for y in range(p.get_height())]


def score_focus_pixbuf(p):
    """Score central detail without reducing the preview's pixel resolution.

    Whole-frame reduction to 512 pixels favored broad, blurred edges in the
    October 11 lens sweep. A native center crop preserves the detail needed to
    distinguish the optically sharper position. Use whole-scene brightness for
    the stability guard: defocusing text can itself change a small crop's mean.
    """
    import gi
    gi.require_version('GdkPixbuf', '2.0')
    from gi.repository import GdkPixbuf
    width, height = min(640, p.get_width()), min(480, p.get_height())
    crop = p.new_subpixbuf((p.get_width()-width)//2, (p.get_height()-height)//2, width, height)
    result = score_rows(pixbuf_rows(crop))
    scene = pixbuf_rows(p.scale_simple(64, 48, GdkPixbuf.InterpType.BILINEAR))
    result['scene_luma'] = sum(map(sum, scene))/(64*48)
    return result


def stable_measurements(values):
    return bool(values) and (
        all(v['controls_before'] == v['controls_after'] == values[0]['controls_before'] for v in values) and
        min(v['luma'] for v in values) > 20 and
        max(v['scene_luma'] for v in values) < max(1, min(v['scene_luma'] for v in values))*1.15)


def verified_focus(values, coarse_score, chosen_score, returned_score):
    """Reject a choice that loses sharpness during refinement or on return."""
    return (stable_measurements(values) and chosen_score > 0 and
            chosen_score >= coarse_score*.85 and .85 <= returned_score/chosen_score <= 1.15)


def score_file(path):
    import gi
    gi.require_version('GdkPixbuf', '2.0')
    from gi.repository import GdkPixbuf
    # At 256px, broad edges outweighed fine detail and selected a visibly
    # softer rear-camera frame. Retain more detail at 512px before smoothing.
    p = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(path), 512, 380, False)
    pixels, stride, channels = p.get_pixels(), p.get_rowstride(), p.get_n_channels()
    if channels not in (3, 4) or p.get_bits_per_sample() != 8:
        raise ValueError('Expected 8-bit RGB JPEG')
    rows = [[(77*pixels[y*stride+x*channels] + 150*pixels[y*stride+x*channels+1] +
              29*pixels[y*stride+x*channels+2])/256
             for x in range(p.get_width())] for y in range(p.get_height())]
    return score_rows(rows)


if __name__ == '__main__':
    print(json.dumps({p: score_file(Path(p)) for p in sys.argv[1:]}, indent=2))
