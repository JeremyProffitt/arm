import argparse
import math
import unittest

from luma.bench import duration, sensor_snapshot
from luma.control import Reading, SENSOR_NAMES


class BenchTests(unittest.TestCase):
    def test_snapshot_preserves_physical_channel_order(self):
        samples = {name: Reading(300 + index, 1) for index, name in enumerate(SENSOR_NAMES)}
        result = sensor_snapshot(samples, 1.1)
        self.assertEqual([r["mux_channel"] for r in result.values()], list(range(5)))
        self.assertTrue(all(r["state"] == "ok" for r in result.values()))
        self.assertEqual(result["rear"]["mux_channel"], 3)

    def test_missing_invalid_stale_and_near_are_explicit(self):
        samples = {
            "left": Reading(None, 1), "right": Reading(1000, 0),
            "rear": Reading(50, 1), "down": Reading(math.nan, 1),
        }
        result = sensor_snapshot(samples, 1)
        self.assertEqual([r["state"] for r in result.values()],
                         ["missing", "invalid", "stale", "near", "invalid"])
        self.assertIsNone(result["down"]["mm"])

    def test_duration_rejects_nonfinite_and_out_of_bounds(self):
        for value in ("nan", "inf", "0", "-1", "601"):
            with self.assertRaises(argparse.ArgumentTypeError):
                duration(value)
        self.assertEqual(duration("10"), 10)


if __name__ == "__main__":
    unittest.main()
