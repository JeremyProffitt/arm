import argparse
import math
import unittest

from luma.bench import build_parser, duration, pulse_width, sensor_snapshot, servo_duration
from luma.control import Reading, SENSOR_NAMES


class BenchTests(unittest.TestCase):
    def test_snapshot_preserves_physical_channel_order(self):
        samples = {name: Reading(300 + index, 1) for index, name in enumerate(SENSOR_NAMES)}
        result = sensor_snapshot(samples, 1.1)
        self.assertEqual([r["mux_channel"] for r in result.values()], list(range(5)))
        self.assertTrue(all(r["state"] == "ok" for r in result.values()))
        self.assertEqual(result["rear_right"]["mux_channel"], 3)

    def test_missing_invalid_stale_and_near_are_explicit(self):
        samples = {
            "front_left": Reading(None, 1), "rear_left": Reading(1000, 0),
            "rear_right": Reading(50, 1), "front_right": Reading(math.nan, 1),
        }
        result = sensor_snapshot(samples, 1)
        self.assertEqual([r["state"] for r in result.values()],
                         ["missing", "invalid", "stale", "near", "invalid"])
        self.assertIsNone(result["front_right"]["mm"])

    def test_duration_rejects_nonfinite_and_out_of_bounds(self):
        for value in ("nan", "inf", "0", "-1", "601"):
            with self.assertRaises(argparse.ArgumentTypeError):
                duration(value)
        self.assertEqual(duration("10"), 10)

    def test_servo_check_is_bounded_and_requires_explicit_confirmation(self):
        for value in ("0","11","nan"):
            with self.assertRaises(argparse.ArgumentTypeError): servo_duration(value)
        for value in ("499","2501"):
            with self.assertRaises(argparse.ArgumentTypeError): pulse_width(value)
        args=build_parser().parse_args(["servo","--joint","yaw","--confirm-unloaded"])
        self.assertTrue(args.confirm_unloaded)
        self.assertEqual(args.pulse_us,1500)


if __name__ == "__main__":
    unittest.main()
