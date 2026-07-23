"""Synthetic multi-channel EEG generator, used in place of real hardware.

Replace `EEGSimulator` with a reader from BrainFlow (OpenBCI) or pylsl (Muse/LSL
streams) once you have a device: anything that produces the same
(n_channels, n_samples) float array per call will work with the rest of the
pipeline unchanged.
"""

import numpy as np

BANDS = {
    "delta": (1, 4),
    "theta": (4, 8),
    "alpha": (8, 13),
    "beta": (13, 30),
    "gamma": (30, 45),
}


class EEGSimulator:
    def __init__(self, n_channels=4, sample_rate=250, band_power=None,
                 noise_level=0.3, drift_period_s=30.0, seed=None):
        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.band_power = band_power or {
            "delta": 0.6, "theta": 0.5, "alpha": 0.8, "beta": 0.4, "gamma": 0.2,
        }
        self.noise_level = noise_level
        self.drift_period_s = drift_period_s

        rng = np.random.default_rng(seed)
        self._rng = rng
        self._t = 0.0
        self._alpha_drift_phase = rng.uniform(0, 2 * np.pi)
        # Fixed per-channel frequency/phase per band so the signal stays
        # continuous across chunks; only amplitude is modulated over time.
        self._band_freqs = {b: rng.uniform(lo, hi, size=n_channels) for b, (lo, hi) in BANDS.items()}
        self._band_phases = {b: rng.uniform(0, 2 * np.pi, size=n_channels) for b in BANDS}

    def next_chunk(self, n_samples):
        """Return the next (n_channels, n_samples) chunk of synthetic EEG."""
        t = self._t + np.arange(n_samples) / self.sample_rate
        chunk = np.zeros((self.n_channels, n_samples))

        # Alpha power slowly rises and falls, simulating a person relaxing
        # and tensing, so the feedback score has something to respond to.
        drift = 0.5 + 0.5 * np.sin(2 * np.pi * t / self.drift_period_s + self._alpha_drift_phase)

        for band, (_, __) in BANDS.items():
            base_amp = self.band_power.get(band, 0.0)
            if base_amp <= 0:
                continue
            amp = base_amp * (0.4 + 0.6 * drift) if band == "alpha" else base_amp
            freqs = self._band_freqs[band]
            phases = self._band_phases[band]
            osc = np.sin(2 * np.pi * freqs[:, None] * t[None, :] + phases[:, None])
            chunk += amp * osc if np.isscalar(amp) else amp[None, :] * osc

        chunk += self._rng.normal(0, self.noise_level, size=chunk.shape)
        self._t += n_samples / self.sample_rate
        return chunk
