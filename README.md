# Sentinel Vision

Local, real-time face recognition POC. Opens a webcam, detects faces live with
InsightFace, compares them against a small local watchlist and labels each face
**POTENTIAL MATCH** or **UNKNOWN**.

Engineering rules live in `CLAUDE.md`, `ARCHITECTURE.md`, `DESIGN_SYSTEM.md`.
Operational state lives in `SENTINEL_VISION_HANDOFF.md`. Durable decisions in
`docs/adr/`.

## Quickstart

```bash
pip install -e .

# add a "wanted" subject (consented) — show one face, press SPACE, ESC to quit
sentinel-vision-enroll "Abdraman"

# start the app (q or Esc to quit)
sentinel-vision
```

Check the commands are installed (PowerShell):

```powershell
Get-Command sentinel-vision
Get-Command sentinel-vision-enroll
```

First launch downloads the InsightFace model. Subjects live under
`data/watchlist/<name>/` (git-ignored); a clear single-face image can also be
dropped there manually.

## Cameras

Every camera is a numeric **index** — add `--camera N` to any command (default 0):

```bash
sentinel-vision --camera 1
sentinel-vision-enroll "Abdraman" --camera 1
sentinel-vision-probe --camera 1          # measure range/quality
```

- **Phone as webcam** — install a webcam app (iPhone: Camo; Android: Iriun or
  DroidCam), connect by **USB** (lowest latency) or **Wi-Fi**; it shows up as a
  new index.
- **Real USB camera** — plug it in; it is another index.
- **Wi-Fi / IP camera (RTSP)** — pass the stream URL (PC and camera on the same
  network; test the URL in VLC first). Credentials are never logged.

  ```bash
  sentinel-vision --source "rtsp://USER:PASS@192.168.1.50:554/stream1"
  ```

  To keep the password out of shell history / process list, set it via the
  environment instead of `--source`:

  ```bash
  export SENTINEL_CAMERA_URL="rtsp://USER:PASS@192.168.1.50:554/stream1"
  sentinel-vision
  ```

  Credentials are masked in all messages.

  On an **unstable network**, a dropped stream auto-reconnects and a stalled read
  times out instead of hanging (`stream_timeout_ms`, `reconnect_attempts`,
  `reconnect_backoff`). See `docs/adr/ADR-006`.

- **Several cameras (e.g. one per floor)** — run **one instance per camera**:

  ```bash
  sentinel-vision --source "rtsp://USER:PASS@192.168.1.51:554/stream1"   # floor 1
  sentinel-vision --source "rtsp://USER:PASS@192.168.1.52:554/stream1"   # floor 2
  ```

  One window per camera. A single process driving many cameras at once is out of
  scope (CPU-bound; would need a GPU). A new camera **type** plugs in by adding a
  `FrameSource` in `bootstrap/frame_source.py` — see `docs/adr/ADR-005`.

## Test

```bash
pytest          # hardware-free unit tests
ruff check .
mypy
```

## Layout

```
src/sentinel_vision/
  config.py                                        # technical config (single source)
  recognition/
    domain/        face_observation, face_embedding, watchlist,
                   face_quality_gate, recognition_policy, recognition_result
    application/   face_analyzer (port), recognize_frame, enroll_subject,
                   face_tracking
    infrastructure/vision/insightface_face_analyzer
    infrastructure/watchlist/local_watchlist_loader, local_watchlist_writer
    infrastructure/presentation/overlay, status_screen
  bootstrap/       frame_source (FrameSource port + adapters),
                   main, enroll, distance_probe
```

## Reliability

Precision-first decision. A face is recognized only when it is close and large
enough (`min_face_pixels`) with a confident detection (`min_detection_score`) —
a distant face shows **MOVE CLOSER** instead of a guess, at recognition and at
enrollment. The match threshold (`recognition_threshold = 0.45`) sits well above
the impostor similarities measured so far. A technical failure (including an
invalid embedding) shows **RECOGNITION UNAVAILABLE**, never a fake UNKNOWN.

This is a **provisional** calibration: FAR/FRR are not yet established and
genuine-acceptance (recall) still needs validation on real enrolled volunteers.
The gate measures size and detection confidence only — not sharpness, pose or
occlusion. See `docs/adr/ADR-002`.

## Capture on match (opt-in, local)

Save a cropped snapshot when a match is **confirmed** — off by default, local only:

```bash
sentinel-vision --capture
```

One photo per subject per `capture_cooldown_seconds` (default 30s), written to
`data/captures/<subject>/<timestamp>_<camera>_<score>.jpg` (git-ignored). Set
`AppConfig.camera_name` (e.g. `"garden"`) to tag the location — a fixed camera's
position is static, so there is no GPS. Snapshots are biometric data: you own
retention and access. Network sending (email/Telegram) is intentionally not
included. See `docs/adr/ADR-007`.

## Notify by email on match (opt-in)

Email on each **confirmed** match — off by default, SMTP credentials from the
environment (never on the command line), sent in the **background** so the live
loop never blocks:

```bash
export SENTINEL_SMTP_HOST="smtp.gmail.com"
export SENTINEL_SMTP_PORT="587"
export SENTINEL_SMTP_USER="you@gmail.com"
export SENTINEL_SMTP_PASSWORD="app-password"
export SENTINEL_SMTP_FROM="you@gmail.com"
export SENTINEL_SMTP_TO="you@gmail.com"
sentinel-vision --capture --notify
```

Same debounce as capture (one per subject per cooldown). Best-effort: a failed
send is logged, not retried — the **local snapshot is the durable record**.
Adding another channel (Telegram, webhook) is a new `EmailSender`-style adapter
+ sink, no change to recognition (OCP). See `docs/adr/ADR-008`.

## Distance / range test

Measure, on your real webcam, how far **detection** and **reliable recognition**
reach. Each face shows its pixel size, detection score, and whether it is
large enough for comparison (`SIZE OK`, green) or below the size gate
(`TOO SMALL`, amber). Passing this gate is not proof of a correct identity match:

```bash
sentinel-vision-probe                                  # defaults
sentinel-vision-probe --width 1920 --height 1080 --det-size 640
# fallback without reinstall:
python -m sentinel_vision.bootstrap.distance_probe --det-size 640
```

Range is bounded by physics, not software: recognition needs a face of about
`min_face_pixels` (112 px) reaching the model. How far that is depends on sensor
resolution and lens. Detection reaches farther than reliable recognition. The
levers for more range are higher capture resolution, a larger `--det-size`, and
optical zoom — each traded against FPS; measure before adopting. Non-consensual
or long-range surveillance identification is out of scope (`CLAUDE.md §1.1`).

## Performance

Default pack is `buffalo_s` for a smooth CPU demo (~14 FPS, one face). Set
`AppConfig.model_name = "buffalo_l"` for higher accuracy at a large CPU cost.
See `docs/adr/ADR-001`.
