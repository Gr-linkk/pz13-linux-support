/* SPDX-License-Identifier: LGPL-2.1-or-later */
#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <functional>
#include <vector>

namespace libcamera {

/* A bounded contrast search for the PZ13's verified rear actuator range. No DAC
 * value is presented as a diopter. All calls occur on the camera manager thread;
 * samples carry capture timestamps so queued frames cannot score a later move.
 */
class Pz13Af
{
public:
	enum State { Idle, Scanning, Focused, Failed };
	using Move = std::function<bool(int)>;
	using Read = std::function<int()>;
	Pz13Af(Read read, Move move) : read_(read), move_(move) {}
	void start() { *this = Pz13Af(read_, move_); running_ = true; }
	void stop() { running_ = false; phase_ = None; state_ = Idle; }
	void mode(int value)
	{
		if ((value != 1 && value != 2) || value == mode_)
			return;
		mode_ = value;
		phase_ = None;
		state_ = Idle;
		paused_ = false;
		if (mode_ == 2)
			trigger();
	}
	void trigger()
	{
		if (running_ && !fault_ && state_ != Scanning) {
			state_ = Scanning;
			phase_ = Warmup;
			warmup_ = 0;
		}
	}
	void cancel() { phase_ = None; state_ = Idle; }
	void pause(bool pause)
	{
		if (paused_ == pause)
			return;
		paused_ = pause;
		if (pause) {
			phase_ = None;
			if (state_ == Scanning) state_ = Failed;
		} else if (mode_ == 2) {
			state_ = Idle;
			trigger();
		}
	}
	int mode() const { return mode_; }
	State state() const { return state_; }
	bool paused() const { return paused_; }
	bool holdingExposure() const { return phase_ == Coarse || phase_ == Fine || phase_ == Verify; }

	void sample(double captured, double now, double score, double luma, double scene)
	{
		if (!running_ || fault_ || paused_ || !std::isfinite(score) ||
		    !std::isfinite(scene) || !std::isfinite(luma))
			return;
		if (phase_ == None) {
			/* A stable scene never causes periodic hunting. Require a sustained
			 * loss/change, with a cooldown after either success or failure.
			 */
			bool changed = score < referenceScore_ * .65 ||
				       std::abs(scene - referenceScene_) > std::max(20., referenceScene_ * .3);
			if (mode_ == 2 && now > finished_ + 8 && changed) {
				if (!changedSince_) changedSince_ = now;
				if (now - changedSince_ > 1.5) trigger();
			} else {
				changedSince_ = 0;
			}
			return;
		}
		if (phase_ == Warmup) {
			if (!warmup_) warmup_ = now;
			if (now - warmup_ < 1.5) return;
			original_ = read_();
			if (original_ < 265 || original_ > 508) { fault(); return; }
			referenceScore_ = score;
			referenceScene_ = scene;
			if (luma < 20 || score < .0002) { finish(false, now, score, scene); return; }
			positions_ = {265, 296, 326, 357, 387, 418, 448, 478, 508};
			index_ = 0;
			bestScore_ = 0;
			minScene_ = maxScene_ = scene;
			began_ = now;
			phase_ = Coarse;
			move(positions_[0], now);
			return;
		}
		if (now - began_ > 30) { reject(now); return; }
		if (captured < moved_ + .65 || captured < lastSample_ + .08) return;
		lastSample_ = captured;
		minScene_ = std::min(minScene_, scene);
		maxScene_ = std::max(maxScene_, scene);
		if (luma < 20 || maxScene_ > std::max(1., minScene_) * 1.15) {
			reject(now);
			return;
		}
		samples_.push_back(score);
		if (samples_.size() < 3) return;
		std::sort(samples_.begin(), samples_.end());
		double measured = samples_[1];
		if (phase_ == Verify) {
			if (measured < bestScore_ * .85 || measured > bestScore_ * 1.15)
				reject(now);
			else
				finish(true, now, measured, scene);
			return;
		}
		if (measured > bestScore_) {
			bestScore_ = measured;
			bestPosition_ = positions_[index_];
		}
		if (++index_ < positions_.size()) {
			move(positions_[index_], now);
			return;
		}
		if (phase_ == Coarse) {
			positions_.clear();
			for (int delta : {-10, -5, 5, 10}) {
				int position = bestPosition_ + delta;
				if (position >= 265 && position <= 508) positions_.push_back(position);
			}
			index_ = 0;
			phase_ = Fine;
			move(positions_[0], now);
		} else {
			phase_ = Verify;
			move(bestPosition_, now);
		}
	}

private:
	enum Phase { None, Warmup, Coarse, Fine, Verify };
	void fault() { fault_ = true; phase_ = None; state_ = Failed; }
	void move(int value, double now)
	{
		if (value < 265 || value > 508 || !move_(value)) { fault(); return; }
		moved_ = now;
		samples_.clear();
	}
	void finish(bool ok, double now, double score, double scene)
	{
		phase_ = None;
		state_ = ok ? Focused : Failed;
		finished_ = now;
		changedSince_ = 0;
		referenceScore_ = score;
		referenceScene_ = scene;
	}
	void reject(double now)
	{
		if (!move_(original_)) { fault(); return; }
		finish(false, now, referenceScore_, referenceScene_);
	}
	Read read_;
	Move move_;
	Phase phase_ = None;
	State state_ = Idle;
	bool running_ = false, fault_ = false, paused_ = false;
	int mode_ = 1, original_ = 265, bestPosition_ = 265;
	size_t index_ = 0;
	std::vector<int> positions_;
	std::vector<double> samples_;
	double warmup_ = 0, began_ = 0, moved_ = 0, lastSample_ = 0, finished_ = 0;
	double bestScore_ = 0, referenceScore_ = 0, referenceScene_ = 0;
	double minScene_ = 0, maxScene_ = 0, changedSince_ = 0;
};

} /* namespace libcamera */
