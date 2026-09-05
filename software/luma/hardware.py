"""Raspberry Pi 4 adapters. Importing behavior code needs no hardware packages."""
import math
import subprocess
import time
from contextlib import ExitStack
from .control import Reading, SENSOR_NAMES, LIMITS
from .servo_bus import ServoBus, ServoError


def validate_config(config, arm):
    for field in ("neutral_ticks", "joint_signs"):
        if len(config.get(field, [])) != 4:
            raise ValueError(f"{field} must contain four values")
    if any(type(v) is not int or not 400 <= v <= 3695 for v in config["neutral_ticks"]):
        raise ValueError("neutral positions must leave room for limited motion")
    if any(v not in (-1, 1) for v in config["joint_signs"]):
        raise ValueError("joint_signs must be +1 or -1")
    if not 0 <= config["outer_brightness"] <= 0.20:
        raise ValueError("Outer RGB brightness is limited to 20%")
    if not 0 <= config["inner_brightness"] <= 1.0:
        raise ValueError("Inner white brightness must be between0 and1")
    if arm and config.get("calibrated") is not True:
        raise ValueError("Complete unloaded joint calibration before setting calibrated=true")
    display_kind = config.get("display_kind", "usb_serial")
    if display_kind not in ("usb_serial", "dsi"):
        raise ValueError(f"display_kind must be usb_serial or dsi, got {display_kind!r}")
    for key in ("servo_port", "display_port"):
        if key == "display_port" and display_kind != "usb_serial":
            continue
        if "SET_TO_" in config[key]:
            raise ValueError(f"Set {key} to the actual /dev/serial/by-id device")


class Ranging:
    def __init__(self):
        import board, adafruit_tca9548a, adafruit_vl53l1x
        self.i2c = board.I2C()
        mux = adafruit_tca9548a.TCA9548A(self.i2c, address=0x70)
        self.devices = []
        try:
            for channel in range(5):
                sensor = adafruit_vl53l1x.VL53L1X(mux[channel])
                self.devices.append(sensor)
                sensor.distance_mode = 1
                sensor.timing_budget = 33
                sensor.stop_ranging()
        except BaseException:
            self.close()
            raise
        self.samples = {}
        self.active = 0
        self.started = None

    def poll(self, now):
        # One emitter ranges at a time: the mux alone cannot prevent optical crosstalk.
        sensor = self.devices[self.active]
        name = SENSOR_NAMES[self.active]
        if self.started is None:
            sensor.start_ranging()
            self.started = now
        elif sensor.data_ready:
            cm = sensor.distance
            self.samples[name] = Reading(None if cm is None else cm * 10.0, now)
            sensor.clear_interrupt()
            sensor.stop_ranging()
            self.active = (self.active + 1) % 5
            self.started = None
        elif now - self.started > 0.12:
            self.samples[name] = Reading(None, now)
            sensor.stop_ranging()
            self.active = (self.active + 1) % 5
            self.started = None
        return self.samples

    def close(self):
        for sensor in self.devices:
            try:
                sensor.stop_ranging()
            except OSError:
                pass


class Display:
    def __init__(self, port):
        import serial
        self.io = serial.Serial(port, 115200, timeout=0, write_timeout=0.05)
        self.last_rx = time.monotonic()
        self.seen_reply = False
        self.last_tx = -100.0
        self.face = None
        self.buffer = b""

    def update(self, now, face):
        pending = self.io.in_waiting
        if pending:
            self.buffer += self.io.read(min(pending, 512))
            while b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                if line.strip() in (b"PONG", b"READY LUMA1") or line.startswith(b"OK "):
                    self.last_rx = now
                    self.seen_reply = True
            self.buffer = self.buffer[-256:]
        if face != self.face:
            self.io.write(f"FACE {face}\n".encode("ascii"))
            self.face = face
        if now - self.last_tx > 0.25:
            self.io.write(b"PING\n")
            self.last_tx = now
        return self.seen_reply and now - self.last_rx < 1.5

    def close(self):
        self.io.close()


class Hardware:
    def __init__(self, config, arm=False):
        validate_config(config, arm)
        self.cleanup = ExitStack()
        self.config = config
        self.armed = False
        self.ticks = None
        self.bus = None
        self.audio = None
        self.speech = None
        try:
            self._open()
        except BaseException:
            self.cleanup.close()
            raise

    def _open(self):
        import board, neopixel, neopixel_spi
        from gpiozero import DigitalInputDevice
        config = self.config
        self.estop = DigitalInputDevice(27, pull_up=True)
        self.cleanup.callback(self.estop.close)
        self.outer = neopixel_spi.NeoPixel_SPI(board.SPI(), 60, bpp=3,
            pixel_order=neopixel_spi.GRB, brightness=config["outer_brightness"], auto_write=False)
        self.cleanup.callback(self._blank, self.outer, (0,0,0))
        self.inner = neopixel.NeoPixel(board.D18, 24, bpp=4,
            pixel_order=neopixel.GRBW, brightness=config["inner_brightness"], auto_write=False)
        self.cleanup.callback(self._blank, self.inner, (0,0,0,0))
        self.outer.fill((0,0,0)); self.outer.show()
        self.inner.fill((0,0,0,0)); self.inner.show()
        if config.get("display_kind", "usb_serial") == "dsi":
            from .face import DsiDisplay
            self.display = DsiDisplay()
        else:
            self.display = Display(config["display_port"])
        self.cleanup.callback(self.display.close)
        self.bus = ServoBus(config["servo_port"])
        self.cleanup.callback(self.bus.close)
        self.ranging = Ranging()
        self.cleanup.callback(self.ranging.close)
        self.last_feedback = 0
        self.feedback_good = False
        self._check_feedback(time.monotonic())

    @staticmethod
    def _blank(strip, black):
        try:
            strip.fill(black)
            strip.show()
        finally:
            strip.deinit()

    def arm(self):
        # Called only after all five sensor samples and face heartbeat pass preflight.
        if self.config.get("calibrated") is not True:
            raise RuntimeError("Joint calibration is not complete")
        if self.stop_open():
            raise RuntimeError("Motor stop circuit open")
        self._check_feedback(time.monotonic())
        if not self.feedback_good or any(abs(a-b)>34 for a,b in zip(self.ticks,self.config["neutral_ticks"])):
            raise RuntimeError("Support arm and place within 3 degrees of indexed neutral before arming")
        self.bus.move(self.ticks)
        self.bus.torque(True)
        self.armed = True
        return tuple((t-n)*360/(4096*s) for t,n,s in
                     zip(self.ticks,self.config["neutral_ticks"],self.config["joint_signs"]))

    def hold(self):
        if self.armed:
            try:
                self.ticks = self.bus.positions()
            except (ServoError, OSError):
                pass
            try:
                if self.ticks is not None:
                    self.bus.move(self.ticks)
            finally:
                self.armed = False

    def _check_feedback(self, now):
        self.ticks = self.bus.positions()
        self.feedback_good = all(abs(t-n) <= (limit+4)*4096/360
            for t,n,limit in zip(self.ticks,self.config["neutral_ticks"],LIMITS))
        self.last_feedback = now

    def stop_open(self):
        # gpiozero's .value is logical active-low when pull_up=True; read the
        # physical level explicitly. NC2 grounded=0 normal; open/broken=1 stop.
        return bool(self.estop.pin.state)

    def poll(self, now):
        readings = self.ranging.poll(now)
        if now - self.last_feedback > 0.1:
            try:
                self._check_feedback(now)
            except (ServoError, OSError):
                self.feedback_good = False
        return readings, self.stop_open(), self.feedback_good

    def write(self, output, now):
        ok = self.display.update(now, output.face)
        self.outer.fill(output.rgb); self.outer.show()
        self.inner.fill(white_pixel(output.white)); self.inner.show()
        if self.armed:
            if output.fault:
                self.hold()
            else:
                ticks = [round(n+s*a*4096/360) for n,s,a in
                    zip(self.config["neutral_ticks"], self.config["joint_signs"], output.angles)]
                self.bus.move(ticks)
        if output.say_hi and (self.audio is None or self.audio.poll() is not None):
            # Direct argument vector: no shell expansion and no network TTS service.
            self.speech = subprocess.Popen(["espeak-ng", "--stdout", "-s", "155", "-p", "65", "Hi!"],
                                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            self.audio = subprocess.Popen(["aplay", "-q", "-D", self.config["audio_device"]],
                                          stdin=self.speech.stdout, stdout=subprocess.DEVNULL,
                                          stderr=subprocess.DEVNULL)
            self.speech.stdout.close()
        return ok

    def close(self):
        try:
            self.hold()
        finally:
            try:
                self.cleanup.close()
            finally:
                for process in (self.audio,self.speech):
                    if process is not None and process.poll() is None:
                        process.terminate()


def white_pixel(value):
    if type(value) is not int or not 0 <= value <= 192:
        raise ValueError("White channel must be an integer0..192")
    return (0,0,0,value)
