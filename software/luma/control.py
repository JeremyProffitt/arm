"""Deterministic behavior model. Distances are millimeters, angles are degrees.

The five ranging sensors are interaction inputs, not a safety-rated perimeter.
Faults freeze commanded motion. A physical motor supply stop remains independent.
"""
from dataclasses import dataclass
import math

SENSOR_NAMES = ("front", "front_left", "rear_left", "rear_right", "front_right")
JOINT_NAMES = ("yaw", "shoulder", "elbow", "wrist")
LIMITS = (25.0, 10.0, 10.0, 10.0)
SCENES = ("idle", "wink", "hi", "happy")


@dataclass(frozen=True)
class Reading:
    mm: float | None
    stamp: float


@dataclass(frozen=True)
class Output:
    angles: tuple[float, ...]
    face: str
    rgb: tuple[int, int, int]
    white: int
    fault: str | None
    say_hi: bool = False


class Controller:
    def __init__(self, *, armed=False):
        self.armed = armed
        self.angles = (0.0,) * 4
        self.fault = None
        self.scene = "idle"
        self.scene_start = 0.0
        self.last_time = None
        self.last_gesture = -100.0
        self._say_pending = False

    def play(self, scene: str, now: float):
        if scene not in SCENES:
            raise ValueError(f"Unknown scene: {scene}")
        self.scene, self.scene_start = scene, now
        self._say_pending = scene == "hi"

    def trip(self, reason: str):
        self.fault = self.fault or reason
        self._say_pending = False

    def step(self, now: float, readings: dict[str, Reading], *, estop=False,
             display_ok=True, servo_ok=True) -> Output:
        dt = 0.0 if self.last_time is None else now - self.last_time
        self.last_time = now
        if not math.isfinite(now) or dt < 0 or dt > 0.5:
            self.trip("control timing gap")
        if estop:
            self.trip("motor stop open")
        if not display_ok:
            self.trip("display heartbeat missing")
        if not servo_ok:
            self.trip("servo PWM controller communication lost")
        for name in SENSOR_NAMES:
            r = readings.get(name)
            if r is None or not math.isfinite(r.stamp) or not 0 <= now - r.stamp <= 0.65:
                self.trip(f"{name}: stale sensor")
            elif r.mm is None or not math.isfinite(r.mm) or not 30 <= r.mm <= 4000:
                self.trip(f"{name}: invalid range")
            elif r.mm < 100:
                self.trip(f"{name}: near obstruction")
        if self.fault:
            return Output(self.angles, "fault", (255, 25, 0), 0, self.fault)

        if self.scene == "idle" and now - self.last_gesture > 8:
            # A hand at the rear requests a wink; a person in front requests Hi.
            if min(readings["rear_left"].mm, readings["rear_right"].mm) < 250:
                self.play("wink", now)
                self.last_gesture = now
            elif readings["front"].mm < 650:
                self.play("hi", now)
                self.last_gesture = now
            elif min(readings["front_left"].mm, readings["front_right"].mm) < 350:
                self.play("happy", now)
                self.last_gesture = now
        t = max(0.0, now - self.scene_start)
        if t >= 6.0:
            self.scene = "idle"
        target = [0.0] * 4
        rgb = (30, 150, 220)
        if self.scene == "wink":
            target[3] = 7.0 * math.sin(math.pi * min(t / 3, 1))
            rgb = (180, 65, 240)
        elif self.scene == "hi":
            target[0] = 12.0 * math.sin(2 * math.pi * t / 3) * min(t, 1) * max(0, min(6-t, 1))
            target[3] = 5.0 * math.sin(math.pi * t / 3)
            rgb = (20, 230, 200)
        elif self.scene == "happy":
            target[1] = 4.0 * math.sin(2 * math.pi * t / 2.5)
            target[2] = -target[1]
            target[3] = 6.0 * math.sin(2 * math.pi * t / 2.5)
            rgb = (255, 155, 30)
        if self.armed:
            # 12 deg/s command slew; servo hardware is separately speed limited.
            step = 12.0 * min(max(dt, 0), 0.05)
            self.angles = tuple(max(-limit, min(limit, old + max(-step, min(step, new-old))))
                                for old, new, limit in zip(self.angles, target, LIMITS))
        say = self._say_pending
        self._say_pending = False
        return Output(self.angles, self.scene, rgb, 192, None, say)
