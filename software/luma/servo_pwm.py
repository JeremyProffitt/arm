"""PCA9685 control for four Miuzei DS3218MG 270-degree position servos.

The PCA9685 confirms only controller communication. The servos provide no
position, load, current, or temperature telemetry.
"""
import math


SERVO_COUNT = 4
PWM_FREQUENCY_HZ = 50
MIN_PULSE_US = 500
MAX_PULSE_US = 2500
ANGLE_SPAN_DEG = 270.0
US_PER_DEGREE = (MAX_PULSE_US - MIN_PULSE_US) / ANGLE_SPAN_DEG


class ServoError(RuntimeError):
    pass


def pulse_to_duty_cycle(pulse_us, frequency_hz=PWM_FREQUENCY_HZ):
    if isinstance(pulse_us, bool) or not isinstance(pulse_us, (int, float)):
        raise ValueError("pulse width must be a number")
    if not math.isfinite(pulse_us) or not MIN_PULSE_US <= pulse_us <= MAX_PULSE_US:
        raise ValueError("pulse width outside DS3218 range")
    if not 1 <= frequency_hz <= 330:
        raise ValueError("PWM frequency outside supported range")
    return round(pulse_us * frequency_hz * 65535 / 1_000_000)


def angles_to_pulses(neutral_pulse_us, joint_signs, angles):
    if not all(len(values) == SERVO_COUNT for values in (neutral_pulse_us, joint_signs, angles)):
        raise ValueError("expected four servo values")
    pulses = [round(neutral + sign * angle * US_PER_DEGREE)
              for neutral, sign, angle in zip(neutral_pulse_us, joint_signs, angles)]
    if any(not MIN_PULSE_US <= pulse <= MAX_PULSE_US for pulse in pulses):
        raise ValueError("servo target outside DS3218 pulse range")
    return pulses


class ServoPwm:
    def __init__(self, i2c, channels, address=0x40):
        if (len(channels) != SERVO_COUNT or len(set(channels)) != SERVO_COUNT
                or any(type(channel) is not int or not 0 <= channel < 16 for channel in channels)):
            raise ValueError("servo channels must be four unique PCA9685 channels")
        from adafruit_pca9685 import PCA9685
        self.channels = tuple(channels)
        self.pca = None
        try:
            self.pca = PCA9685(i2c, address=address)
            self.pca.frequency = PWM_FREQUENCY_HZ
            self.disable()
        except (OSError, ValueError, ServoError) as error:
            if self.pca is not None:
                self.pca.deinit()
            raise ServoError(f"PCA9685 initialization failed: {error}") from error

    def move(self, pulses):
        if len(pulses) != SERVO_COUNT:
            raise ValueError("expected four servo pulse widths")
        duties = [pulse_to_duty_cycle(pulse) for pulse in pulses]
        try:
            for channel, duty in zip(self.channels, duties):
                self.pca.channels[channel].duty_cycle = duty
        except OSError as error:
            raise ServoError(f"PCA9685 write failed: {error}") from error

    def move_one(self, joint_index, pulse_us):
        if type(joint_index) is not int or not 0 <= joint_index < SERVO_COUNT:
            raise ValueError("joint index must be0 through3")
        duty = pulse_to_duty_cycle(pulse_us)
        self.disable()
        try:
            self.pca.channels[self.channels[joint_index]].duty_cycle = duty
        except OSError as error:
            raise ServoError(f"PCA9685 write failed: {error}") from error

    def disable(self):
        try:
            for channel in self.channels:
                self.pca.channels[channel].duty_cycle = 0
        except OSError as error:
            raise ServoError(f"PCA9685 disable failed: {error}") from error

    def healthy(self):
        try:
            mode = int(self.pca.mode1_reg)
            frequency = float(self.pca.frequency)
            return bool(mode & 0x20) and abs(frequency - PWM_FREQUENCY_HZ) < 1.0
        except (OSError, TypeError, ValueError):
            return False

    def close(self):
        self.pca.deinit()
