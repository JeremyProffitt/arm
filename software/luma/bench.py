"""Focused hardware checks; servo output requires an explicit unloaded confirmation."""
import argparse
import json
import math
from pathlib import Path
import sys
import time

from .control import JOINT_NAMES, SCENES, SENSOR_NAMES
from .hardware import Display, Ranging
from .servo_pwm import MAX_PULSE_US, MIN_PULSE_US, ServoPwm


def duration(value):
    seconds = float(value)
    if not math.isfinite(seconds) or not 0 < seconds <= 600:
        raise argparse.ArgumentTypeError("seconds must be finite and between 0 and 600")
    return seconds


def servo_duration(value):
    seconds = float(value)
    if not math.isfinite(seconds) or not 0 < seconds <= 10:
        raise argparse.ArgumentTypeError("servo seconds must be finite and between0 and10")
    return seconds


def pulse_width(value):
    pulse = int(value)
    if not MIN_PULSE_US <= pulse <= MAX_PULSE_US:
        raise argparse.ArgumentTypeError("pulse must be between500 and2500us")
    return pulse


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


def display(port, seconds, scene, kind="usb_serial"):
    if kind == "dsi":
        from .face import DsiDisplay
        screen = DsiDisplay()
    else:
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


def servo(config_path, joint, pulse_us, seconds):
    import board
    config = json.loads(config_path.read_text())
    i2c = board.I2C()
    controller = None
    try:
        controller = ServoPwm(i2c, config["servo_channels"], config["pca9685_address"])
        index = JOINT_NAMES.index(joint)
        controller.move_one(index, pulse_us)
        print(json.dumps({"check":"servo","joint":joint,"channel":config["servo_channels"][index],
                          "pulse_us":pulse_us,"seconds":seconds,"warning":"unloaded output active"}),flush=True)
        time.sleep(seconds)
        return 0
    finally:
        try:
            if controller is not None:
                controller.disable()
        finally:
            try:
                if controller is not None:
                    controller.close()
            finally:
                i2c.deinit()


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    sensor_parser = commands.add_parser("sensors", help="Poll all five mux channels without motors or LED rings")
    sensor_parser.add_argument("--seconds", type=duration, default=10.0)
    display_parser = commands.add_parser("display", help="Check display heartbeat and request animated faces")
    display_parser.add_argument("--port", default=None,
        help="Actual USB serial device; /dev/serial/by-id/... on Pi. Required unless --kind dsi")
    display_parser.add_argument("--kind", choices=("usb_serial", "dsi"), default="usb_serial",
        help="usb_serial talks to the ESP32 face board; dsi renders locally on the Waveshare panel")
    display_parser.add_argument("--seconds", type=duration, default=10.0)
    display_parser.add_argument("--scene", choices=("all", *SCENES, "fault"), default="all")
    servo_parser = commands.add_parser("servo", help="Center one unloaded DS3218MG through the PCA9685")
    servo_parser.add_argument("--config", type=Path,
        default=Path(__file__).resolve().parents[1]/"config.json")
    servo_parser.add_argument("--joint", choices=JOINT_NAMES, required=True)
    servo_parser.add_argument("--pulse-us", type=pulse_width, default=1500)
    servo_parser.add_argument("--seconds", type=servo_duration, default=2.0)
    servo_parser.add_argument("--confirm-unloaded", action="store_true",
        help="required: servo horn is disconnected from the arm and the motor stop is in reach")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "display" and args.kind == "usb_serial" and not args.port:
        parser.error("--port is required when --kind usb_serial")
    if args.command == "servo" and not args.confirm_unloaded:
        parser.error("servo check requires --confirm-unloaded")
    try:
        if args.command == "sensors":
            return sensors(args.seconds)
        if args.command == "display":
            return display(args.port, args.seconds, args.scene, args.kind)
        return servo(args.config, args.joint, args.pulse_us, args.seconds)
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"Bench check failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
