"""Small ST3215 protocol driver, based on Waveshare's ST/SMS register map.

No EEPROM configuration or ID changes are made by the runtime. Positions are
single-turn 0..4095, little-endian; all reads validate status ID and checksum.
"""
import time


class ServoError(RuntimeError):
    pass


def packet(servo_id, instruction, parameters=b""):
    if not 0 <= servo_id <= 254:
        raise ValueError("invalid servo ID")
    body = bytes((servo_id, len(parameters)+2, instruction)) + bytes(parameters)
    return b"\xff\xff" + body + bytes((~sum(body) & 255,))


def parse_status(frame, expected_id, expected_payload):
    if len(frame) != expected_payload + 6 or frame[:2] != b"\xff\xff":
        raise ServoError("truncated or malformed status packet")
    if frame[2] != expected_id or frame[3] != expected_payload + 2:
        raise ServoError("wrong servo ID or packet length")
    if sum(frame[2:]) & 255 != 255:
        raise ServoError("servo checksum failure")
    if frame[4]:
        raise ServoError(f"servo {expected_id} status error 0x{frame[4]:02x}")
    return frame[5:-1]


class ServoBus:
    def __init__(self, port):
        import serial
        self.io = serial.Serial(port, 1_000_000, timeout=0.025, write_timeout=0.025)

    def read(self, servo_id, address, size):
        self.io.reset_input_buffer()
        self.io.write(packet(servo_id, 2, bytes((address, size))))
        frame = self.io.read(size + 6)
        return parse_status(frame, servo_id, size)

    def positions(self):
        result = []
        for servo_id in range(1, 5):
            # Present position through temperature: 56..63.
            data = self.read(servo_id, 56, 8)
            position = data[0] | data[1] << 8
            if not 0 <= position <= 4095 or not 90 <= data[6] <= 126 or data[7] >= 65:
                raise ServoError(f"servo {servo_id}: position, voltage or temperature fault")
            result.append(position)
        return result

    def sync(self, address, values):
        width = len(next(iter(values.values())))
        if any(len(v) != width for v in values.values()):
            raise ValueError("sync write widths differ")
        data = bytes((address, width)) + b"".join(bytes((sid,))+bytes(v) for sid, v in values.items())
        self.io.write(packet(254, 0x83, data))

    def torque(self, enabled):
        self.sync(40, {sid: bytes((int(enabled),)) for sid in range(1, 5)})

    def move(self, ticks):
        if len(ticks) != 4 or any(not 0 <= p <= 4095 for p in ticks):
            raise ValueError("invalid four-joint target")
        # ACC=10; goal position, time=0, speed=140 ticks/s (~12.3 deg/s).
        self.sync(41, {sid: bytes((10,))+int(p).to_bytes(2,"little")+b"\x00\x00\x8c\x00"
                       for sid, p in enumerate(ticks, 1)})

    def close(self):
        self.io.close()
