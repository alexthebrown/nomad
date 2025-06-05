# src/speaker.py
import pyttsx3
import threading
import time

class Speaker:
    def __init__(self, led_controller=None):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 160)
        self.led_controller = led_controller

        # Try to set male voice
        voices = self.engine.getProperty("voices")
        for voice in voices:
            if "alex" in voice.name.lower() or "male" in voice.name.lower():
                self.engine.setProperty("voice", voice.id)
                break

    def speak(self, text):
        if self.led_controller:
            led_thread = threading.Thread(target=self._pulse_leds)
            led_thread.start()

        self.engine.say(text)
        self.engine.runAndWait()

        if self.led_controller:
            self.led_controller.off()

    def _pulse_leds(self):
        # Simulated LED pulsing during speech
        while self.engine._inLoop:
            for level in [0.3, 0.6, 1.0, 0.6]:
                self.led_controller.flash(level, duration=0.1)
            time.sleep(0.05)
