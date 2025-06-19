import time
import board
import neopixel
import random

# --- NeoPixel Configuration ---
# LED strip configuration:
LED_COUNT      = 24      # Number of LED pixels.
LED_PIN        = board.D18 # GPIO pin connected to the pixels (18 is default for NeoPixels on RPi).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz).
LED_DMA        = 10      # DMA channel to use for generating signal (try 10).
LED_BRIGHTNESS = 0.5     # Set to 0.0 for darkest and 1.0 for brightest.
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift).
LED_CHANNEL    = 0       # Set to 0 for GPIOs 10, 12, 18, 20 and 21.
                         # Set to 1 for GPIOs 13, 19, 21, 22, 24, 26. (RPi 3/4 uses 1 for D13, D19)


# Create NeoPixel object with appropriate configuration.
# This initializes the strip.
pixels = neopixel.NeoPixel(
    LED_PIN,
    LED_COUNT,
    brightness=LED_BRIGHTNESS,
    auto_write=False, # We will manually call .show() for animations
    pixel_order=neopixel.GRB # Often NeoPixels are GRB, but could be RGB
)

print(f"NeoPixel strip initialized with {LED_COUNT} LEDs on GPIO {LED_PIN}.")

# --- Helper Functions for Colors ---
def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def color_rgb(r, g, b):
    """Combine R, G, B values into a single integer color."""
    return (r, g, b)

# --- Animation Functions ---

def color_wipe(pixels, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    print(f"Starting Color Wipe: {color}")
    for i in range(LED_COUNT):
        pixels[i] = color
        pixels.show()
        time.sleep(wait_ms / 1000.0)
    print("Color Wipe finished.")

def rainbow_cycle(pixels, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    print(f"Starting Rainbow Cycle for {iterations} iterations.")
    for j in range(256 * iterations):
        for i in range(LED_COUNT):
            pixels[i] = wheel((i + j) & 255)
        pixels.show()
        time.sleep(wait_ms / 1000.0)
    print("Rainbow Cycle finished.")

def theater_chase(pixels, color, wait_ms=50):
    """Movie theater light style chaser animation."""
    print(f"Starting Theater Chase: {color}")
    for q in range(3):
        for i in range(0, LED_COUNT, 3):
            pixels[i+q] = color
        pixels.show()
        time.sleep(wait_ms / 1000.0)
        for i in range(0, LED_COUNT, 3):
            pixels[i+q] = (0, 0, 0) # Turn off
    print("Theater Chase finished.")

def pulse_color(pixels, color, pulse_time_s=2, steps=50):
    """Pulses a single color in and out."""
    print(f"Starting Pulse: {color}")
    for _ in range(2): # Pulse twice
        # Fade in
        for i in range(steps):
            brightness = i / float(steps)
            pixels.fill(tuple(int(c * brightness) for c in color))
            pixels.show()
            time.sleep(pulse_time_s / (steps * 2))

        # Fade out
        for i in range(steps - 1, -1, -1):
            brightness = i / float(steps)
            pixels.fill(tuple(int(c * brightness) for c in color))
            pixels.show()
            time.sleep(pulse_time_s / (steps * 2))
    pixels.fill((0, 0, 0)) # Ensure off at end of pulse
    pixels.show()
    print("Pulse finished.")

def random_sparkle(pixels, spark_count=5, wait_ms=50, duration_s=10):
    """Randomly lights up a few pixels with random colors."""
    print(f"Starting Random Sparkle for {duration_s} seconds.")
    start_time = time.time()
    while (time.time() - start_time) < duration_s:
        pixels.fill((0, 0, 0)) # Clear all
        sparkles_on = []
        for _ in range(spark_count):
            idx = random.randint(0, LED_COUNT - 1)
            # Ensure unique pixels for sparkles, or allow overlap
            if idx not in sparkles_on:
                pixels[idx] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                sparkles_on.append(idx)
        pixels.show()
        time.sleep(wait_ms / 1000.0)
    pixels.fill((0, 0, 0)) # Clear at end
    pixels.show()
    print("Random Sparkle finished.")

def chasing_dots(pixels, num_dots=3, color=(255, 255, 255), speed_ms=50):
    """Multiple dots chasing along the strip."""
    print(f"Starting Chasing Dots: {color}")
    for k in range(LED_COUNT + num_dots): # Run for one full cycle + dots to clear
        pixels.fill((0, 0, 0)) # Clear all pixels

        for i in range(num_dots):
            idx = (k - i + LED_COUNT) % LED_COUNT
            if 0 <= idx < LED_COUNT:
                pixels[idx] = color
        pixels.show()
        time.sleep(speed_ms / 1000.0)
    print("Chasing Dots finished.")


# --- Main Loop to Run Animations ---
if __name__ == '__main__':
    print('Press Ctrl-C to quit.')
    try:
        while True:
            # Clear the strip before each animation for clean transitions
            pixels.fill((0, 0, 0))
            pixels.show()
            time.sleep(0.5)

            color_wipe(pixels, (255, 0, 0))  # Red
            color_wipe(pixels, (0, 255, 0))  # Green
            color_wipe(pixels, (0, 0, 255))  # Blue

            rainbow_cycle(pixels, wait_ms=20, iterations=1) # One full rainbow cycle

            theater_chase(pixels, (127, 127, 127)) # White
            theater_chase(pixels, (127,   0,   0)) # Red
            theater_chase(pixels, (  0,   0, 127)) # Blue

            pulse_color(pixels, (255, 255, 0)) # Yellow pulse
            pulse_color(pixels, (0, 255, 255)) # Cyan pulse

            random_sparkle(pixels, duration_s=15) # Sparkle for 15 seconds

            chasing_dots(pixels, num_dots=3, color=(255, 0, 255), speed_ms=75) # Magenta chasing dots
            chasing_dots(pixels, num_dots=5, color=(0, 255, 0), speed_ms=50) # Green chasing dots

    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        # Turn all LEDs off cleanly on exit.
        print("Clearing LEDs...")
        pixels.fill((0, 0, 0))
        pixels.show()
        print("LEDs off. Program terminated.")

