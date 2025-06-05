# src/led_controller.py

import time
import os
import platform

class LEDController:
    def __init__(self, pins=None, simulate=True):
        self.simulate = simulate or platform.system() != "Linux"
        self.led_count = len(pins) if pins else 8

    def flash(self, level, duration=0.1):
        if self.simulate:
            bar = self._make_bar(level)
            print(f"\r[LEDs] {bar}", end="", flush=True)
            time.sleep(duration)
        else:
            # You can expand this later to support real GPIO on Pi
            pass

    def off(self):
        if self.simulate:
            print("\r[LEDs] " + " " * self.led_count + "\r", end="", flush=True)

    def _make_bar(self, level):
        on_count = int(level * self.led_count)
        return "█" * on_count + "-" * (self.led_count - on_count)

    def cleanup(self):
        self.off()
