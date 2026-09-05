import argparse
import json
from pathlib import Path
import time
from .control import Controller, Reading, SENSOR_NAMES, SCENES


def main():
    parser = argparse.ArgumentParser(description="LUMA Pi4 master. Simulation is the default.")
    parser.add_argument("--hardware", action="store_true")
    parser.add_argument("--arm", action="store_true", help="enable calibrated joints; requires --hardware")
    parser.add_argument("--scene", choices=SCENES, default="idle")
    parser.add_argument("--seconds", type=float, default=8)
    parser.add_argument("--config", type=Path, default=Path(__file__).resolve().parents[1]/"config.json")
    args = parser.parse_args()
    if args.arm and not args.hardware:
        parser.error("--arm requires --hardware")
    if args.seconds <= 0:
        parser.error("--seconds must be positive")
    controller = Controller(armed=not args.hardware)
    io = None
    display_ok = True
    try:
        if args.hardware:
            from .hardware import Hardware
            io = Hardware(json.loads(args.config.read_text()), arm=args.arm)
            # All five channels must be fresh before torque can be enabled.
            deadline = time.monotonic()+1.5
            samples = {}
            while len(samples)<5 and time.monotonic()<deadline:
                samples, estop, servo_ok = io.poll(time.monotonic())
                display_ok = io.display.update(time.monotonic(), "idle")
                time.sleep(0.005)
            now = time.monotonic()
            preflight = Controller().step(now,samples,estop=estop,servo_ok=servo_ok,display_ok=display_ok)
            if args.arm:
                if preflight.fault:
                    raise RuntimeError(f"Arming refused: {preflight.fault}")
                controller.angles = io.arm()
                controller.armed = True
        start = time.monotonic() if io else 0.0
        controller.play(args.scene, start)
        frame = 0
        while True:
            now = time.monotonic() if io else frame/50.0
            if now - start >= args.seconds:
                break
            if io:
                samples, estop, servo_ok = io.poll(now)
            else:
                samples = {name: Reading(1000, now) for name in SENSOR_NAMES}
                estop, servo_ok = False, True
            output = controller.step(now, samples, estop=estop, display_ok=display_ok, servo_ok=servo_ok)
            if io:
                display_ok = io.write(output, now)
                time.sleep(0.02)
            if frame % 10 == 0 or output.say_hi:
                print(json.dumps({"t": round(now-start,3), "face": output.face,
                    "angles_deg": [round(a,2) for a in output.angles], "rgb": output.rgb,
                    "white": output.white, "say_hi": output.say_hi, "fault": output.fault}))
            frame += 1
    except KeyboardInterrupt:
        pass
    finally:
        if io:
            io.close()


if __name__ == "__main__":
    main()
