# src/led_controller.py
import board
import neopixel
import time

# Parameters
LED_COUNT = 8       # Change to match your number of LEDs
LED_PIN = board.D18 # GPIO 18 (PWM required)
BRIGHTNESS = 0.5    # 0.0 to 1.0
ORDER = neopixel.GRB

# Initialize the NeoPixel strip
pixels = neopixel.NeoPixel(
    LED_PIN, LED_COUNT, brightness=BRIGHTNESS, auto_write=False, pixel_order=ORDER
)

# Example animations
def rainbow_cycle(wait=0.05):
    for j in range(255):
        for i in range(LED_COUNT):
            rc_index = (i * 256 // LED_COUNT) + j
            pixels[i] = wheel(rc_index & 255)
        pixels.show()
        time.sleep(wait)

def wheel(pos):
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

# Example: Blink all LEDs red
def blink_red():
    for _ in range(3):
        pixels.fill((255, 0, 0))
        pixels.show()
        time.sleep(0.5)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(0.5)

if __name__ == "__main__":
    blink_red()
    rainbow_cycle()
