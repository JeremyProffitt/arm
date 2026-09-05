import math
import unittest
from luma.control import Controller, Reading, SENSOR_NAMES, LIMITS
from luma.servo_bus import packet, parse_status, ServoError
from luma.hardware import validate_config, white_pixel, Hardware
from types import SimpleNamespace


def clear(now=0):
    return {name: Reading(1000, now) for name in SENSOR_NAMES}


class ControllerTests(unittest.TestCase):
    def test_all_scenes_respect_limits_and_speed(self):
        for scene in ("wink", "hi", "happy"):
            c = Controller(armed=True)
            c.play(scene, 0)
            last = (0,)*4
            for i in range(500):
                out = c.step(i/50, clear(i/50))
                self.assertIsNone(out.fault)
                for a,b,limit in zip(out.angles,last,LIMITS):
                    self.assertLessEqual(abs(a),limit)
                    self.assertLessEqual(abs(a-b),0.240001)
                last = out.angles

    def test_fault_latches_and_freezes(self):
        c = Controller(armed=True); c.play("hi",0)
        c.step(0,clear()); before = c.step(.02,clear(.02))
        s = clear(.04); s["left"] = Reading(45,.04)
        out = c.step(.04,s)
        self.assertEqual(out.angles,before.angles)
        self.assertIn("obstruction",out.fault)
        self.assertEqual(c.step(.06,clear(.06)).fault,out.fault)

    def test_each_sensor_is_required(self):
        for name in SENSOR_NAMES:
            s = clear(); del s[name]
            self.assertIn(name,Controller().step(0,s).fault)

    def test_nan_none_and_stale_are_not_clear_space(self):
        for reading in (Reading(None,0),Reading(float("nan"),0),Reading(1000,-1),Reading(1000,1)):
            s = clear(); s["down"] = reading
            self.assertIsNotNone(Controller().step(0,s).fault)

    def test_estop_display_and_servo_faults(self):
        for kw in ({"estop":True},{"display_ok":False},{"servo_ok":False}):
            self.assertIsNotNone(Controller().step(0,clear(),**kw).fault)

    def test_large_scheduler_gap_freezes(self):
        c=Controller(); c.step(0,clear())
        self.assertIn("timing",c.step(1,clear(1)).fault)

    def test_hi_speaks_once(self):
        c=Controller(); c.play("hi",0)
        self.assertTrue(c.step(0,clear()).say_hi)
        self.assertFalse(c.step(.02,clear(.02)).say_hi)

    def test_unarmed_never_moves(self):
        c=Controller(); c.play("happy",0)
        for i in range(100):
            self.assertEqual(c.step(i/50,clear(i/50)).angles,(0,)*4)


class ProtocolTests(unittest.TestCase):
    def test_known_read_request(self):
        self.assertEqual(packet(1,2,b"\x38\x02"), bytes.fromhex("ffff0104023802be"))

    def test_checked_response(self):
        frame=packet(1,0,b"\x00\x08")
        self.assertEqual(parse_status(frame,1,2),b"\x00\x08")
        for bad in (frame[:-1],frame[:-1]+b"\x00",packet(2,0,b"\x00\x08"),packet(1,4,b"\x00\x08")):
            with self.assertRaises(ServoError): parse_status(bad,1,2)

    def test_config_refuses_uncalibrated_motion(self):
        c={"calibrated":False,"neutral_ticks":[2048]*4,"joint_signs":[1]*4,
           "outer_brightness":.2,"inner_brightness":.2,"servo_port":"A","display_port":"B"}
        validate_config(c,False)
        with self.assertRaises(ValueError): validate_config(c,True)
        c["calibrated"]=True; c["outer_brightness"]=.3
        with self.assertRaises(ValueError): validate_config(c,True)

    def test_inner_ring_only_white_and_capped(self):
        for value in (0,80,192):
            self.assertEqual(white_pixel(value),(0,0,0,value))
        for value in (-1,193,255,float("nan")):
            with self.assertRaises(ValueError): white_pixel(value)

    def test_stop_uses_physical_level_not_active_low_gpiozero_value(self):
        h=Hardware.__new__(Hardware)
        h.estop=SimpleNamespace(pin=SimpleNamespace(state=0),value=1)
        self.assertFalse(h.stop_open())
        h.estop.pin.state=1
        self.assertTrue(h.stop_open())

    def test_hold_reads_actual_pose_before_command(self):
        h=Hardware.__new__(Hardware)
        h.armed=True; h.ticks=[2048]*4
        commands=[]
        h.bus=SimpleNamespace(positions=lambda:[2050,2060,2070,2080],move=commands.append)
        h.hold()
        self.assertEqual(commands,[[2050,2060,2070,2080]])
        self.assertFalse(h.armed)

    def test_hold_falls_back_to_last_feedback_on_read_failure(self):
        def failed(): raise ServoError("timeout")
        h=Hardware.__new__(Hardware)
        h.armed=True; h.ticks=[2049]*4
        commands=[]
        h.bus=SimpleNamespace(positions=failed,move=commands.append)
        h.hold()
        self.assertEqual(commands,[[2049]*4])
        self.assertFalse(h.armed)


if __name__ == "__main__": unittest.main()
