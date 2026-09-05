# Verification record

Date:2026-09-04. Development host:Windows, Python3.13.14.

`python -m unittest discover -s tests -v`: **18 tests passed**. Coverage includes three-scene joint limits and12°/s slew, required readings from all five sensors, stale/NaN/no-return and close-object faults, latched hold, motor stop polarity, missing display/servo feedback, one-shot Hi speech event, exact RGBW white-only output limit, servo packet checksum/status handling, calibration refusal, fresh measured-position hold, last-feedback fallback when a hold read times out, bench sensor/channel reporting and bounded diagnostic duration.

`python -m luma.bench --help` and both subcommand help screens load without Pi-only dependencies. Independent sensor/display bench adapters are provided; actual diagnostic operation still requires the physical boards.

`python -m luma.app --scene hi --seconds 1`: JSON output showed one Hi event, bounded yaw/wrist motion, W192 and no faults. The wink/happy numerical trajectories are also covered by the scene tests for500 frames each.

Physical Pi hardware, servos, optical measurements, stop relay wiring and thermal operation were not available in this workspace and have not been tested. The Raspberry Pi adapters are implemented against the vendor protocols/APIs but remain bench-validation work.

The display source targets the exact Waveshare SKU28514, with vendor-derived initialization for both documented panel IDs. **Cross-compilation is not verified.** The PlatformIO invocation did not reach compilation because the GCC dependency download stalled and restarted; an alternate range download returned truncated data, and a direct official-source download timed out. Those build attempts were stopped without flashing a device. No firmware binary or physical display test is claimed. PlatformIO build dependencies and incomplete downloads are excluded from the deliverable archive.

## 2026-09-05 update: optional Pi-rendered DSI head

Added `luma/face.py` (`draw_face`, `DsiDisplay`) for the optional Waveshare4inch DSI LCD(C) head, where the Pi renders the face itself instead of delegating to the ESP32 board. `draw_face` reproduces `paint()` from `display_firmware/src/main.cpp` pixel-for-pixel logic (same rounded-rect eyes, blink/wink timing, happy-face arcs, Hi mouth animation and fault/offline WAITING/PAUSED banner), scaled from the firmware's360x360 canvas to any target surface size — 720x720 for the real panel. `DsiDisplay` mirrors the USB `Display` adapter's `update(now, face) -> bool` / `close()` contract, so `Hardware._open` and `luma.bench.display` pick either implementation via the new `display_kind` config/`--kind` CLI value (`usb_serial` default, or `dsi`) without changing any caller in `luma/control.py` or `luma/app.py`. `pygame` is imported only inside `luma/face.py`, and only reached lazily (inside `Hardware._open` / `bench.display`) when a DSI head is actually selected — `luma.hardware` and the rest of the behavior code import cleanly with no pygame dependency, verified by a subprocess check that `"pygame" not in sys.modules` after `import luma.hardware`.

`python -m unittest discover -s tests -v`: **34 tests passed** (the prior18 plus16 new tests in `tests/test_face.py` covering `draw_face` pixel output for idle/wink/happy/hi/fault/offline scenes, `DsiDisplay.update()`/`close()` against pygame's `dummy` SDL video driver, `validate_config` accepting/rejecting `display_kind` values, and `luma.bench`'s new `--kind` argument handling). Pixel assertions sample exact eye/blush/mouth/alert-bar centers and one point on the happy-face eye arc, matching coordinates converted directly from `main.cpp`'s draw calls.

Physical DSI panel operation (actual Waveshare4inch DSI LCD(C) hardware, `kmsdrm` output, `/boot/firmware/config.txt` overlays) was not available in this workspace and has not been tested; `DsiDisplay` was only exercised against pygame's headless `dummy` driver. `pygame-ce2.5.8` is confirmed installed in the development `.venv` and is pinned as the `dsi` optional dependency group in `pyproject.toml`.
