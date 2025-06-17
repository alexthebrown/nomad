import time
import board
import neopixel
import random
import threading

LED_COUNT = 24  # Assuming 4 sides * 6 LEDs/side = 24 LEDs
LED_PIN = board.D18

pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)

LEDS_PER_SIDE = 6
NUM_SIDES = 4

# Define your two colors for the top two LEDs on each side
TOP_LED_COLOR_1 = (209, 77, 77)  # Example: Red
TOP_LED_COLOR_2 = (227, 220, 11)  # Example: Yellow

def breathe_color(color, duration=2.0, steps=50):
    for i in range(steps + 1):
        brightness = i / steps
        r, g, b = color
        breathed_color = (int(r * brightness), int(g * brightness), int(b * brightness))
        yield breathed_color
    for i in range(steps, -1, -1):
        brightness = i / steps
        r, g, b = color
        breathed_color = (int(r * brightness), int(g * brightness), int(b * brightness))
        yield breathed_color

def set_top_leds(color1, color2):
    for side in range(NUM_SIDES):
        start_index = side * LEDS_PER_SIDE
        pixels[start_index] = color1
        pixels[start_index + 1] = color2

def set_random_leds(color):
    for i in range(2, LEDS_PER_SIDE):
        if random.random() < 0.5:
            for side in range(NUM_SIDES):
                pixels[side * LEDS_PER_SIDE + i] = color
        else:
            for side in range(NUM_SIDES):
                pixels[side * LEDS_PER_SIDE + i] = (0, 0, 0)

def random_pattern_thread():
    while True:
        set_random_leds((119, 209, 77))
        pixels.show()
        time.sleep(random.uniform(0.1, 0.5))

if __name__ == "__main__":
    random_thread = threading.Thread(target=random_pattern_thread, daemon=True)
    random_thread.start()

    try:
        while True:
            # Breathe with color 1 for the first LED and color 2 for the second
            for breathed_color1 in breathe_color(TOP_LED_COLOR_1):
                breathed_color2_gen = breathe_color(TOP_LED_COLOR_2)
                try:
                    breathed_color2 = next(breathed_color2_gen)
                except StopIteration:
                    breathed_color2_gen = breathe_color(TOP_LED_COLOR_2)
                    breathed_color2 = next(breathed_color2_gen)

                set_top_leds(breathed_color1, breathed_color2)
                pixels.show()
                time.sleep(0.04)

    except KeyboardInterrupt:
        pixels.fill((0, 0, 0))
        pixels.show()
