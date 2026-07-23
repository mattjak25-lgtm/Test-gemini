"""Realtime neurofeedback server.

Streams simulated EEG through the band-power + scoring pipeline and pushes
feedback metrics to connected browsers over WebSocket, at UPDATE_HZ. Each
session is logged to a CSV under recordings/.
"""

import asyncio
import csv
import json
import time
from pathlib import Path

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from .processing import band_powers, FeedbackScorer
from .simulator import EEGSimulator, BANDS

SAMPLE_RATE = 250
UPDATE_HZ = 10.0
WINDOW_SECONDS = 2.0

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
RECORDINGS_DIR = Path(__file__).resolve().parent.parent / "recordings"

app = FastAPI()


class SessionRecorder:
    def __init__(self):
        RECORDINGS_DIR.mkdir(exist_ok=True)
        path = RECORDINGS_DIR / f"session_{int(time.time())}.csv"
        self._file = open(path, "w", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow(["timestamp", *BANDS.keys(), "feedback_score"])

    def log(self, timestamp, powers, score):
        self._writer.writerow([timestamp, *[powers[b] for b in BANDS], score])
        self._file.flush()

    def close(self):
        self._file.close()


async def eeg_stream(send_text):
    simulator = EEGSimulator(n_channels=4, sample_rate=SAMPLE_RATE)
    scorer = FeedbackScorer(target_band="alpha")
    recorder = SessionRecorder()

    chunk_samples = int(SAMPLE_RATE / UPDATE_HZ)
    window_samples = int(SAMPLE_RATE * WINDOW_SECONDS)
    buffer = np.zeros((simulator.n_channels, 0))
    start = time.time()

    try:
        while True:
            chunk = simulator.next_chunk(chunk_samples)
            buffer = np.concatenate([buffer, chunk], axis=1)[:, -window_samples:]
            if buffer.shape[1] >= window_samples:
                powers = band_powers(buffer, SAMPLE_RATE)
                score = scorer.update(powers)
                payload = {"t": time.time() - start, "bands": powers, "score": score}
                recorder.log(payload["t"], powers, score)
                await send_text(json.dumps(payload))
            await asyncio.sleep(1 / UPDATE_HZ)
    finally:
        recorder.close()


@app.get("/")
async def index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        await eeg_stream(websocket.send_text)
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000)
