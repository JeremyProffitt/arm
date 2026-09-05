# Verification record

Date:2026-09-04. Development host:Windows, Python3.13.14.

`python -m unittest discover -s tests -v`: **18 tests passed**. Coverage includes three-scene joint limits and12°/s slew, required readings from all five sensors, stale/NaN/no-return and close-object faults, latched hold, motor stop polarity, missing display/servo feedback, one-shot Hi speech event, exact RGBW white-only output limit, servo packet checksum/status handling, calibration refusal, fresh measured-position hold, last-feedback fallback when a hold read times out, bench sensor/channel reporting and bounded diagnostic duration.

`python -m luma.bench --help` and both subcommand help screens load without Pi-only dependencies. Independent sensor/display bench adapters are provided; actual diagnostic operation still requires the physical boards.

`python -m luma.app --scene hi --seconds 1`: JSON output showed one Hi event, bounded yaw/wrist motion, W192 and no faults. The wink/happy numerical trajectories are also covered by the scene tests for500 frames each.

Physical Pi hardware, servos, optical measurements, stop relay wiring and thermal operation were not available in this workspace and have not been tested. The Raspberry Pi adapters are implemented against the vendor protocols/APIs but remain bench-validation work.

The display source targets the exact Waveshare SKU28514, with vendor-derived initialization for both documented panel IDs. **Cross-compilation is not verified.** The PlatformIO invocation did not reach compilation because the GCC dependency download stalled and restarted; an alternate range download returned truncated data, and a direct official-source download timed out. Those build attempts were stopped without flashing a device. No firmware binary or physical display test is claimed. PlatformIO build dependencies and incomplete downloads are excluded from the deliverable archive.
