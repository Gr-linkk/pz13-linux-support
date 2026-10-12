/* SPDX-License-Identifier: LGPL-2.1-or-later */
#include "pz13_af.h"
#include "pz13_focus_measure.h"
#include <cassert>
#include <iostream>

using libcamera::Pz13Af;

int main()
{
	int position = 350, moves = 0;
	bool actuatorGood = true;
	Pz13Af af([&] { return position; }, [&](int value) {
		assert(value >= 265 && value <= 508);
		++moves;
		if (!actuatorGood) return false;
		position = value;
		return true;
	});
	auto step = [&](double t, double scene = 100., double multiplier = 1.) {
		double score = .01 + .04 * std::exp(-std::pow((position - 286.) / 35., 2));
		af.sample(t, t, multiplier * score, 100, scene);
	};
	af.start();
	for (int i = 1; i < 50; ++i) step(i * .1);
	assert(moves == 0 && af.state() == Pz13Af::Idle); // Default leaves app manual focus alone.
	af.mode(2);
	for (int i = 50; i < 300; ++i) step(i * .1);
	assert(af.state() == Pz13Af::Focused && position == 286);
	int completedMoves = moves;
	for (int i = 300; i < 700; ++i) step(i * .1);
	assert(moves == completedMoves); // No hunting on a stationary scene.
	for (int i = 700; i < 745; ++i) step(i * .1, 100., .4);
	assert(af.state() == Pz13Af::Scanning && moves > completedMoves);
	af.stop();
	completedMoves = moves;
	for (int i = 745; i < 900; ++i) step(i * .1);
	assert(moves == completedMoves && !af.holdingExposure());

	position = 350;
	af.start(); af.mode(2);
	for (int i = 1; i < 23; ++i) step(i * .1);
	step(2.4, 140.); // Changed illumination must restore the original setting.
	assert(af.state() == Pz13Af::Failed && position == 350 && !af.holdingExposure());

	af.start(); af.mode(2);
	actuatorGood = false;
	for (int i = 1; i < 600; ++i) step(i * .1);
	assert(af.state() == Pz13Af::Failed);
	completedMoves = moves;
	af.mode(1); af.mode(2);
	for (int i = 600; i < 900; ++i) step(i * .1);
	assert(moves == completedMoves); // Physical faults never cause repeated actuator retries.
	actuatorGood = true;

	af.start(); af.mode(2);
	for (int i = 1; i < 22; ++i) step(i * .1);
	completedMoves = moves;
	for (int i = 22; i < 100; ++i) af.sample(0, i * .1, .05, 100, 100);
	assert(moves == completedMoves); // Queued pre-move frames do not advance the scan.
	af.pause(true);
	assert(!af.holdingExposure());
	for (int i = 100; i < 300; ++i) step(i * .1);
	assert(moves == completedMoves);
	af.pause(false);
	for (int i = 300; i < 550; ++i) step(i * .1);
	assert(af.state() == Pz13Af::Focused && position == 286);

	// Contrast metric rejects a flat field, is invariant to channel storage,
	// and prefers focused fine structure over a blurred version.
	const unsigned int w = 640, h = 480;
	std::vector<uint8_t> rgb(w * h * 3, 100), blurred(rgb.size());
	auto flat = libcamera::pz13FocusMeasure(rgb.data(), w, h, w * 3, 3, true, 1);
	assert(flat.score == 0 && flat.luma == 100);
	for (unsigned int y = 0; y < h; ++y)
		for (unsigned int x = 0; x < w; ++x)
			for (unsigned int c = 0; c < 3; ++c) {
				double v = std::sin(x * .6) * std::sin(y * .7);
				rgb[(y * w + x) * 3 + c] = 120 + 70 * v;
				blurred[(y * w + x) * 3 + c] = 120 + 10 * v;
			}
	auto sharp = libcamera::pz13FocusMeasure(rgb.data(), w, h, w * 3, 3, true, 1);
	auto soft = libcamera::pz13FocusMeasure(blurred.data(), w, h, w * 3, 3, true, 1);
	assert(sharp.score > 10 * soft.score);
	assert(libcamera::pz13FocusMeasure(rgb.data(), w, h, w * 3, 3, false, 1).score == sharp.score);
	std::cout << "PZ13 AF state, stale-frame, instability, fault, pause and metric regressions passed\n";
}
