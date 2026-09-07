import math
import unittest
from luma.control import Controller, Reading, SENSOR_NAMES, LIMITS
from luma.hardware import validate_config, white_pixel, Hardware
from luma.servo_pwm import angles_to_pulses, pulse_to_duty_cycle
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
        s = clear(.04); s["front_left"] = Reading(45,.04)
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
            s = clear(); s["front_right"] = reading
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

    def test_rear_pair_and_front_side_channels_drive_gestures(self):
        rear = clear(); rear["rear_left"] = Reading(200,0)
        self.assertEqual(Controller().step(0,rear).face,"wink")
        side = clear(); side["front_right"] = Reading(300,0)
        self.assertEqual(Controller().step(0,side).face,"happy")

    def test_unarmed_never_moves(self):
        c=Controller(); c.play("happy",0)
        for i in range(100):
            self.assertEqual(c.step(i/50,clear(i/50)).angles,(0,)*4)


class PwmTests(unittest.TestCase):
    def test_known_pulse_conversion(self):
        self.assertEqual(pulse_to_duty_cycle(1500), round(1500*50*65535/1_000_000))
        for bad in (499,2501,float("nan"),True,"1500"):
            with self.assertRaises(ValueError): pulse_to_duty_cycle(bad)

    def test_angles_map_across_270_degree_servo_span(self):
        self.assertEqual(angles_to_pulses([1500]*4,[1,-1,1,-1],[27,27,-13.5,-13.5]),
                         [1700,1300,1400,1600])

    def test_config_refuses_uncalibrated_motion(self):
        c={"calibrated":False,"neutral_pulse_us":[1500]*4,"joint_signs":[1]*4,
           "servo_channels":[0,1,2,3],"pca9685_address":0x40,
           "outer_brightness":.2,"inner_brightness":.2,"display_port":"B"}
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

    def test_arm_commands_calibrated_neutral(self):
        h=Hardware.__new__(Hardware)
        h.config={"calibrated":True,"neutral_pulse_us":[1490,1500,1510,1520]}
        h.armed=False; h.servo_good=False
        commands=[]
        h.servos=SimpleNamespace(healthy=lambda:True,move=commands.append)
        h.stop_open=lambda:False
        self.assertEqual(h.arm(),(0.0,)*4)
        self.assertEqual(commands,[[1490,1500,1510,1520]])
        self.assertTrue(h.armed)

    def test_hold_keeps_last_pwm_target(self):
        h=Hardware.__new__(Hardware)
        h.armed=True; h.pulses=[1490,1500,1510,1520]
        h.hold()
        self.assertEqual(h.pulses,[1490,1500,1510,1520])
        self.assertFalse(h.armed)


if __name__ == "__main__": unittest.main()
