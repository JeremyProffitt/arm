import math
import subprocess
import sys
import unittest
from pathlib import Path

from luma.face import draw_face, DsiDisplay, CYAN, BLUSH, ALERT, BLACK  # sets PYGAME_HIDE_SUPPORT_PROMPT
import pygame

from luma.hardware import validate_config
from luma.bench import build_parser, main as bench_main


def pixel(surface, x, y):
    return tuple(surface.get_at((round(x), round(y))))[:3]


class DrawFaceTests(unittest.TestCase):
    def test_idle_shows_open_eyes_on_black(self):
        surface = pygame.Surface((720, 720))
        draw_face(surface, "idle", 0.0)
        self.assertEqual(pixel(surface, 2 * (95 + 24), 2 * (107 + 37)), CYAN)
        self.assertEqual(pixel(surface, 5, 5), BLACK)

    def test_idle_blush(self):
        surface = pygame.Surface((720, 720))
        draw_face(surface, "idle", 0.0)
        self.assertEqual(pixel(surface, 2 * 77, 2 * 207), BLUSH)

    def test_wink_closes_right_eye_mid_cycle(self):
        surface = pygame.Surface((720, 720))
        draw_face(surface, "wink", 1.0)
        self.assertEqual(pixel(surface, 2 * (217 + 24), 2 * (107 + 37)), BLACK)
        self.assertEqual(pixel(surface, 2 * (214 + 27), 2 * (146 + 5)), CYAN)

    def test_wink_eye_open_outside_wink_window(self):
        surface = pygame.Surface((720, 720))
        draw_face(surface, "wink", 0.2)
        self.assertEqual(pixel(surface, 2 * (217 + 24), 2 * (107 + 37)), CYAN)

    def test_happy_uses_arcs_not_eye_rects(self):
        surface = pygame.Surface((720, 720))
        draw_face(surface, "happy", 0.0)
        self.assertEqual(pixel(surface, 2 * (95 + 24), 2 * (107 + 37)), BLACK)
        arc_x = 2 * (119 + 32 * math.cos(4.7))
        arc_y = 2 * (155 + 22 * math.sin(4.7))
        self.assertEqual(pixel(surface, arc_x, arc_y), CYAN)

    def test_fault_shows_alert_bars(self):
        surface = pygame.Surface((720, 720))
        draw_face(surface, "fault", 0.0)
        self.assertEqual(pixel(surface, 2 * (90 + 30), 2 * (136 + 6)), ALERT)

    def test_offline_overrides_face_with_alert(self):
        surface = pygame.Surface((720, 720))
        draw_face(surface, "idle", 0.0, offline=True)
        self.assertEqual(pixel(surface, 2 * (90 + 30), 2 * (136 + 6)), ALERT)

    def test_hi_mouth_circle(self):
        surface = pygame.Surface((720, 720))
        draw_face(surface, "hi", 0.0)
        self.assertEqual(pixel(surface, 360, 464), CYAN)


class DsiDisplayTests(unittest.TestCase):
    def test_update_returns_true_and_redraws_on_new_frame(self):
        display = DsiDisplay(driver="dummy", fullscreen=False)
        try:
            self.assertTrue(display.update(0.0, "idle"))
            self.assertTrue(display.update(2.0, "idle"))
        finally:
            display.close()

    def test_close_does_not_raise(self):
        display = DsiDisplay(driver="dummy", fullscreen=False)
        display.update(0.0, "idle")
        display.close()


class ValidateConfigDisplayKindTests(unittest.TestCase):
    def base_config(self):
        return {
            "calibrated": False, "neutral_ticks": [2048] * 4, "joint_signs": [1] * 4,
            "outer_brightness": .2, "inner_brightness": .2,
            "servo_port": "/dev/serial/by-id/actual-servo",
            "display_port": "/dev/serial/by-id/SET_TO_WAVESHARE_DISPLAY_ID",
        }

    def test_dsi_kind_does_not_require_real_display_port(self):
        c = self.base_config()
        c["display_kind"] = "dsi"
        validate_config(c, False)  # placeholder display_port is fine for dsi

    def test_unknown_display_kind_rejected(self):
        c = self.base_config()
        c["display_kind"] = "spi"
        with self.assertRaises(ValueError):
            validate_config(c, False)

    def test_absent_display_kind_still_requires_real_display_port(self):
        c = self.base_config()  # no display_kind key -> defaults to usb_serial
        with self.assertRaises(ValueError):
            validate_config(c, False)
        c["display_port"] = "/dev/serial/by-id/actual-display"
        validate_config(c, False)


class BenchArgumentTests(unittest.TestCase):
    def test_dsi_kind_does_not_require_port(self):
        args = build_parser().parse_args(["display", "--kind", "dsi"])
        self.assertIsNone(args.port)
        self.assertEqual(args.kind, "dsi")

    def test_usb_serial_kind_without_port_is_rejected(self):
        with self.assertRaises(SystemExit):
            bench_main(["display", "--kind", "usb_serial", "--seconds", "1"])


class HardwareImportTests(unittest.TestCase):
    def test_importing_hardware_does_not_import_pygame(self):
        software_dir = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "-c", "import luma.hardware, sys; print('pygame' in sys.modules)"],
            cwd=str(software_dir), capture_output=True, text=True, check=True,
        )
        self.assertEqual(result.stdout.strip(), "False")


if __name__ == "__main__":
    unittest.main()
