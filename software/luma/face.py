"""Pi-rendered face for the optional Waveshare 4inch DSI LCD (C) head.

This reproduces ``paint()`` from ``display_firmware/src/main.cpp`` in Python so
the Pi itself can draw the face directly onto the round 720x720 DSI panel
instead of delegating to the ESP32 face coprocessor. Coordinates below are the
firmware's 360x360 canvas coordinates; ``draw_face`` scales everything by
``surface.get_width()/360`` so it works on any target surface size.
"""
import math
import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

# Converted from the firmware's RGB565 constants: 0x67DF (cyan), 0xC1EF
# (blush) and 0xFC60 (alert/fault orange).
CYAN = (96, 248, 248)
BLUSH = (192, 60, 120)
ALERT = (248, 140, 0)
BLACK = (0, 0, 0)

_font_cache = {}


def _font(size):
    if not pygame.font.get_init():
        pygame.font.init()
    font = _font_cache.get(size)
    if font is None:
        font = pygame.font.SysFont(None, size)
        _font_cache[size] = font
    return font


def draw_face(surface, face, t, offline=False, blink=False):
    scale = surface.get_width() / 360

    def rect(x, y, w, h, r, color):
        pygame.draw.rect(
            surface, color,
            pygame.Rect(round(x * scale), round(y * scale), round(w * scale), round(h * scale)),
            border_radius=round(r * scale),
        )

    def circle(cx, cy, radius, color):
        pygame.draw.circle(surface, color, (round(cx * scale), round(cy * scale)),
                            max(round(radius * scale), 0))

    def stroke_arc(cx, cy, rx, ry, start, end, width, color):
        a = start
        while a <= end:
            circle(cx + rx * math.cos(a), cy + ry * math.sin(a), width, color)
            a += 0.03

    surface.fill(BLACK)
    fault_or_offline = face == "fault" or offline
    color = ALERT if fault_or_offline else CYAN
    if fault_or_offline:
        rect(90, 136, 60, 12, 6, color)
        rect(210, 136, 60, 12, 6, color)
        rect(150, 235, 60, 9, 4, color)
        font = _font(round(16 * scale))
        text = font.render("WAITING" if offline else "PAUSED", True, color)
        surface.blit(text, (round(120 * scale), round(285 * scale)))
    else:
        wink = face == "wink" and 0.65 < (t % 3) < 1.45
        happy = face == "happy"
        if happy:
            stroke_arc(119, 155, 32, 22, 3.25, 6.15, 6, color)
            stroke_arc(241, 155, 32, 22, 3.25, 6.15, 6, color)
        else:
            if blink:
                rect(92, 146, 54, 10, 5, color)
            else:
                rect(95, 107, 48, 74, 22, color)
            if wink or blink:
                rect(214, 146, 54, 10, 5, color)
            else:
                rect(217, 107, 48, 74, 22, color)
        circle(77, 207, 13, BLUSH)
        circle(283, 207, 13, BLUSH)
        if face == "hi":
            opening = 8 + int(12 * (0.5 + 0.5 * math.sin(t * 12)))
            circle(180, 232, opening, color)
            font = _font(round(24 * scale))
            text = font.render("Hi!", True, color)
            surface.blit(text, (round(155 * scale), round(289 * scale)))
        else:
            stroke_arc(180, 205, 51, 45 if happy else 30, 0.15, 2.99, 6, color)


class DsiDisplay:
    """Drives a pygame window/framebuffer as the face surface for the DSI head.

    Mirrors the USB `Display` adapter's `update`/`close` contract so
    `Hardware` and `bench.display` can use either interchangeably. There is
    no separate microcontroller here, so "heartbeat" becomes "a frame was
    drawn within the last 1.5s" instead of a serial PONG reply.
    """

    def __init__(self, size=(720, 720), driver=None, fullscreen=True):
        if driver is not None:
            os.environ["SDL_VIDEODRIVER"] = driver
        pygame.display.init()
        flags = pygame.FULLSCREEN if (fullscreen and driver is None) else 0
        self.screen = pygame.display.set_mode(size, flags)
        pygame.mouse.set_visible(False)
        self.face = None
        self.face_start = None
        self.last_frame = float("-inf")

    def update(self, now, face):
        if face != self.face:
            self.face = face
            self.face_start = now
        if now - self.last_frame >= 0.04:
            blink = face == "idle" and (now % 5.2) > 5.05
            draw_face(self.screen, face, now - self.face_start, offline=False, blink=blink)
            pygame.display.flip()
            self.last_frame = now
        pygame.event.pump()
        return now - self.last_frame < 1.5

    def close(self):
        pygame.display.quit()
