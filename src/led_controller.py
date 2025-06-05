import RPi.GPIO as GPIO
import time

class LEDController:
    def __init__(self, pins):
        self.pins = pins
        GPIO.setmode(GPIO.BCM)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

    def flash(self, level, duration=0.1):
        # Level: 0.0 to 1.0
        count = int(level * len(self.pins))
        for i, pin in enumerate(self.pins):
            GPIO.output(pin, GPIO.HIGH if i < count else GPIO.LOW)
        time.sleep(duration)
        self.off()

    def off(self):
        for pin in self.pins:
            GPIO.output(pin, GPIO.LOW)

    def cleanup(self):
        self.off()
        GPIO.cleanup()
