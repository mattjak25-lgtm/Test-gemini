# Neurofeedback Trainer

A minimal, runnable neurofeedback pipeline: EEG source → band-power
extraction → feedback score → real-time visual feedback in the browser.
Currently runs entirely on simulated EEG, so no hardware is required to
build and test the pipeline.

## Architecture

```
backend/simulator.py   synthetic multi-channel EEG generator
backend/processing.py  Welch PSD -> band power (delta/theta/alpha/beta/gamma)
                        -> smoothed 0-1 feedback score vs. a rolling baseline
backend/server.py       FastAPI app: runs the pipeline in a loop, streams
                        JSON metrics over WebSocket at 10 Hz, logs each
                        session to recordings/session_<timestamp>.csv
frontend/index.html     self-contained page: an orb that grows/brightens
                        with the feedback score, plus a live band-power
                        bar chart and score history line
```

The default protocol is **alpha up-training**: the feedback score tracks
alpha-band (8-13 Hz) power relative to the user's own rolling 30s baseline,
so relaxing (raising alpha) grows the orb. Score is computed in
`FeedbackScorer` (`backend/processing.py`) and is the only place you need to
change protocol — e.g. swap `target_band="alpha"` for `"theta"`, or write a
custom `update()` that computes a theta/beta ratio instead of a single band.

## Running it

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m backend.server
```

Open http://localhost:8000 — the orb should slowly pulse over a ~30s cycle
(the simulator modulates alpha power on a sine wave so there's something to
see without needing real relaxation).

## Swapping in real hardware

Everything upstream of `band_powers()` only depends on getting a
`(n_channels, n_samples)` float array. To use a real device, replace
`EEGSimulator.next_chunk()` in `backend/server.py`'s `eeg_stream()` loop
with a reader from:

- **[BrainFlow](https://brainflow.org/)** — works with OpenBCI Cyton/Ganglion
  boards; `board.get_current_board_data(chunk_samples)` returns the same
  shape of array.
- **[pylsl](https://github.com/labstreaminglayer/pylsl)** (Lab Streaming
  Layer) — works with Muse headbands via `muselsl` and many research-grade
  amplifiers.

No other code needs to change — `band_powers`, `FeedbackScorer`, the
WebSocket server, and the frontend are all hardware-agnostic.

## Session data

Each run writes a CSV to `recordings/` with per-band power and feedback
score at 10 Hz, useful for reviewing a session's progress or building a
scoring/analytics view later.
