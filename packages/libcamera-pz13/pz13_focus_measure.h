/* SPDX-License-Identifier: LGPL-2.1-or-later */
#pragma once

#include <algorithm>
#include <cstdint>
#include <vector>

namespace libcamera {

struct Pz13FocusMeasure {
	double score = 0, luma = 0, scene = 0;
};

/* Score a fixed central region at the accepted app preview's pixel scale,
 * before resizing to the application's requested output. The small Gaussian
 * filter suppresses Bayer noise without the old whole-frame reduction which
 * favored broad, blurred edges. Buffer geometry is validated by the caller.
 */
inline Pz13FocusMeasure pz13FocusMeasure(const uint8_t *pixels, unsigned int width,
	unsigned int height, unsigned int stride, unsigned int channels, bool rgb,
	unsigned int step = 2)
{
	Pz13FocusMeasure result;
	if (!pixels || (channels != 3 && channels != 4) || !step ||
	    stride < width * channels || width / step < 10 || height / step < 10)
		return result;
	unsigned int w = std::min(640U, width / step), h = std::min(480U, height / step);
	unsigned int ox = (width - w * step) / 2, oy = (height - h * step) / 2;
	auto luma = [&](unsigned int x, unsigned int y) {
		const uint8_t *p = pixels + size_t(y) * stride + x * channels;
		return (77. * p[rgb ? 0 : 2] + 150. * p[1] + 29. * p[rgb ? 2 : 0]) / 256.;
	};
	std::vector<double> gray(w * h), horizontal(w * h), smooth(w * h);
	for (unsigned int y = 0; y < h; ++y)
		for (unsigned int x = 0; x < w; ++x) {
			double sum = 0;
			for (unsigned int dy = 0; dy < step; ++dy)
				for (unsigned int dx = 0; dx < step; ++dx)
					sum += luma(ox + x * step + dx, oy + y * step + dy);
			gray[y * w + x] = sum / (step * step);
		}
	for (unsigned int y = 0; y < h; ++y)
		for (unsigned int x = 1; x + 1 < w; ++x)
			horizontal[y * w + x] = gray[y * w + x - 1] + 2 * gray[y * w + x] + gray[y * w + x + 1];
	for (unsigned int y = 1; y + 1 < h; ++y)
		for (unsigned int x = 1; x + 1 < w; ++x)
			smooth[y * w + x] = (horizontal[(y - 1) * w + x] + 2 * horizontal[y * w + x] + horizontal[(y + 1) * w + x]) / 16;
	unsigned int count = 0;
	for (unsigned int y = h / 5 + 1; y < h * 4 / 5 - 1; ++y)
		for (unsigned int x = w / 5 + 1; x < w * 4 / 5 - 1; ++x) {
			double dx = smooth[y * w + x + 1] - smooth[y * w + x - 1];
			double dy = smooth[(y + 1) * w + x] - smooth[(y - 1) * w + x];
			result.score += dx * dx + dy * dy;
			result.luma += smooth[y * w + x];
			++count;
		}
	result.luma /= count;
	result.score /= count * std::max(1., result.luma * result.luma);
	for (unsigned int y = 0; y < 24; ++y)
		for (unsigned int x = 0; x < 32; ++x)
			result.scene += luma((2 * x + 1) * width / 64, (2 * y + 1) * height / 48);
	result.scene /= 32 * 24;
	return result;
}

} /* namespace libcamera */
