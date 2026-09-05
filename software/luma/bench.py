"""Motor-independent sensor and USB face checks. Never opens the servo bus."""
import argparse
import json
import math
import sys
import time

from .control import SCENES, SENSOR_NAMES
from .hardware import Display, Ranging


def duration(value):
    seconds = float(value)
    if not math.isfinite(seconds) or not 0 < seconds <= 600:
        raise argparse.ArgumentTypeError("seconds must be finite and between 0 and 600")
    return seconds


def sensor_snapshot(samples, now):
    result = {}
    for channel, name in enumerate(SENSOR_NAMES):
        reading = samples.get(name)
        mm, age, state = None, None, "missing"
        if reading is not None:
            age = now - reading.stamp
            if not math.isfinite(age) or not 0 <= age <= 0.65:
                state = "stale"
            elif reading.mm is None or not math.isfinite(reading.mm) or not 30 <= reading.mm <= 4000:
                state = "invalid"
            else:
                mm = round(reading.mm, 1)
                state = "near" if mm < 100 else "ok"
        result[name] = {
            "mux_channel": channel,
            "mm": mm,
            "age_s": round(age, 3) if age is not None and math.isfinite(age) else None,
            "state": state,
        }
    return result


def sensors(seconds):
    ranging = Ranging()
    try:
        start = time.monotonic()
        next_report = start
        samples = {}
        while (now := time.monotonic()) - start < seconds:
            samples = ranging.poll(now)
            if now >= next_report:
                print(json.dumps({"t": round(now - start, 2), "sensors": sensor_snapshot(samples, now)}), flush=True)
                next_report = now + 0.25
            time.sleep(0.005)
        snapshot = sensor_snapshot(samples, time.monotonic())
        passed = all(r["state"] in ("ok", "near") for r in snapshot.values())
        print(json.dumps({"check": "sensors", "passed": passed, "sensors": snapshot}), flush=True)
        # A near range proves communication but is an obstruction in armed operation.
        return 0 if passed else 1
    finally:
        ranging.close()


def display(port, seconds, scene):
    screen = Display(port)
    try:
        start = time.monotonic()
        next_report = start
        healthy = False
        while (now := time.monotonic()) - start < seconds:
            face = SCENES[int((now - start) / 2) % len(SCENES)] if scene == "all" else scene
            healthy = screen.update(now, face)
            if now >= next_report:
                print(json.dumps({"t": round(now - start, 2), "face": face, "heartbeat": healthy}), flush=True)
                next_report = now + 0.5
            time.sleep(0.02)
        print(json.dumps({"check": "display", "passed": healthy}), flush=True)
        return 0 if healthy else 1
    finally:
        screen.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    sensor_parser = commands.add_parser("sensors", help="Poll all five mux channels without motors or LED rings")
    sensor_parser.add_argument("--seconds", type=duration, default=10.0)
    display_parser = commands.add_parser("display", help="Check USB heartbeat and request animated faces")
    display_parser.add_argument("--port", required=True, help="Actual USB serial device; /dev/serial/by-id/... on Pi")
    display_parser.add_argument("--seconds", type=duration, default=10.0)
    display_parser.add_argument("--scene", choices=("all", *SCENES, "fault"), default="all")
    args = parser.parse_args(argv)
    try:
        if args.command == "sensors":
            return sensors(args.seconds)
        return display(args.port, args.seconds, args.scene)
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"Bench check failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
