"""Raspberry Pi 4 adapters. Importing behavior code needs no hardware packages."""
import subprocess
import time
from contextlib import ExitStack
from .control import Reading, SENSOR_NAMES, LIMITS
from .servo_pwm import (
    MAX_PULSE_US, MIN_PULSE_US, US_PER_DEGREE,
    ServoError, ServoPwm, angles_to_pulses, validate_servo_channels,
)


def validate_config(config, arm):
    for field in ("neutral_pulse_us", "joint_signs", "servo_channels"):
        if len(config.get(field, [])) != 4:
            raise ValueError(f"{field} must contain four values")
    if any(type(v) is not int for v in config["neutral_pulse_us"]):
        raise ValueError("neutral pulse widths must be integers")
    for neutral, limit in zip(config["neutral_pulse_us"], LIMITS):
        margin = (limit + 4) * US_PER_DEGREE
        if neutral - margin < MIN_PULSE_US or neutral + margin > MAX_PULSE_US:
            raise ValueError("neutral pulse widths must leave room for limited motion")
    if any(v not in (-1, 1) for v in config["joint_signs"]):
        raise ValueError("joint_signs must be +1 or -1")
    validate_servo_channels(config["servo_channels"])
    if type(config.get("pca9685_address")) is not int or not 0x08 <= config["pca9685_address"] <= 0x77:
        raise ValueError("pca9685_address must be a usable 7-bit I2C address")
    if not 0 <= config["outer_brightness"] <= 0.20:
        raise ValueError("Outer RGB brightness is limited to 20%")
    if not 0 <= config["inner_brightness"] <= 1.0:
        raise ValueError("Inner white brightness must be between0 and1")
    if arm and config.get("calibrated") is not True:
        raise ValueError("Complete unloaded joint calibration before setting calibrated=true")
    display_kind = config.get("display_kind", "usb_serial")
    if display_kind not in ("usb_serial", "dsi"):
        raise ValueError(f"display_kind must be usb_serial or dsi, got {display_kind!r}")
    if display_kind == "usb_serial" and "SET_TO_" in config["display_port"]:
        raise ValueError("Set display_port to the actual /dev/serial/by-id device")


class Ranging:
    def __init__(self, i2c=None):
        import board, adafruit_tca9548a, adafruit_vl53l1x
        self.i2c = i2c or board.I2C()
        self.owns_i2c = i2c is None
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
        if self.owns_i2c:
            self.i2c.deinit()


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
        self.pulses = None
        self.servos = None
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
        self.i2c = board.I2C()
        self.cleanup.callback(self.i2c.deinit)
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
        self.servos = ServoPwm(self.i2c, config["servo_channels"], config["pca9685_address"])
        self.cleanup.callback(self.servos.close)
        self.ranging = Ranging(self.i2c)
        self.cleanup.callback(self.ranging.close)
        self.last_servo_check = 0
        self.servo_good = False
        self._check_servo_controller(time.monotonic())

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
        self._check_servo_controller(time.monotonic())
        if not self.servo_good:
            raise RuntimeError("PCA9685 controller communication failed")
        self.pulses = list(self.config["neutral_pulse_us"])
        self.servos.move(self.pulses)
        self.armed = True
        return (0.0,) * 4

    def hold(self):
        if self.armed:
            # Keep the PCA9685 at the last pulse widths. DS3218 servos have no
            # readable position, so a fault cannot refresh from a measured pose.
            self.armed = False

    def _check_servo_controller(self, now):
        self.servo_good = self.servos.healthy()
        self.last_servo_check = now

    def stop_open(self):
        # gpiozero's .value is logical active-low when pull_up=True; read the
        # physical level explicitly. NC2 grounded=0 normal; open/broken=1 stop.
        return bool(self.estop.pin.state)

    def poll(self, now):
        readings = self.ranging.poll(now)
        if now - self.last_servo_check > 0.1:
            self._check_servo_controller(now)
        return readings, self.stop_open(), self.servo_good

    def write(self, output, now):
        ok = self.display.update(now, output.face)
        self.outer.fill(output.rgb); self.outer.show()
        self.inner.fill(white_pixel(output.white)); self.inner.show()
        if self.armed:
            if output.fault:
                self.hold()
            else:
                self.pulses = angles_to_pulses(
                    self.config["neutral_pulse_us"], self.config["joint_signs"], output.angles)
                try:
                    self.servos.move(self.pulses)
                except ServoError:
                    self.servo_good = False
                    self.armed = False
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
