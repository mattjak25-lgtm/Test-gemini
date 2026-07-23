"""Band-power extraction and feedback scoring."""

import numpy as np
from scipy.integrate import trapezoid
from scipy.signal import welch

from .simulator import BANDS


def band_powers(window, sample_rate):
    """Average band power across channels for one window.

    window: array shaped (n_channels, n_samples)
    Returns: dict of band name -> power
    """
    nperseg = min(window.shape[1], sample_rate * 2)
    freqs, psd = welch(window, fs=sample_rate, nperseg=nperseg, axis=-1)
    psd = psd.mean(axis=0)
    powers = {}
    for band, (lo, hi) in BANDS.items():
        mask = (freqs >= lo) & (freqs < hi)
        powers[band] = float(trapezoid(psd[mask], freqs[mask])) if mask.any() else 0.0
    return powers


class FeedbackScorer:
    """Converts a target band's power into a smoothed 0-1 feedback score,
    relative to a slow-moving baseline (so the score reflects change from the
    user's own recent state rather than an absolute threshold).
    """

    def __init__(self, target_band="alpha", smoothing=0.85, baseline_window_s=30.0, update_rate_hz=10.0):
        self.target_band = target_band
        self.smoothing = smoothing
        self._baseline_decay = 1 - 1 / (baseline_window_s * update_rate_hz)
        self._score = 0.5
        self._baseline = None

    def update(self, powers):
        value = powers.get(self.target_band, 0.0)
        if self._baseline is None:
            self._baseline = value
        else:
            self._baseline = self._baseline_decay * self._baseline + (1 - self._baseline_decay) * value

        baseline = max(self._baseline, 1e-6)
        raw_score = min(max(value / (baseline * 2), 0.0), 1.0)
        self._score = self.smoothing * self._score + (1 - self.smoothing) * raw_score
        return self._score
