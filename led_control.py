import time
import board
import neopixel

# Configure the number of LEDs in your strip
LED_COUNT = 24  # Example: 30 LEDs
# Configure the GPIO pin connected to the data input of the LED strip
LED_PIN = board.D18  # Example: GPIO 18

# Create a NeoPixel object
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)

# Define a function to set the color of a single LED
def set_pixel_color(pixel_num, color):
    pixels[pixel_num] = color
    pixels.show()

# Define a function to set the color of all LEDs
def set_all_pixels(color):
    pixels.fill(color)
    pixels.show()

# Example usage:
# Turn all LEDs red
set_all_pixels((255, 0, 0))
time.sleep(1)

# Turn all LEDs green
set_all_pixels((0, 255, 0))
time.sleep(1)

# Turn all LEDs blue
set_all_pixels((0, 0, 255))
time.sleep(1)

# Set individual LEDs to different colors
set_pixel_color(0, (255, 255, 255))  # First LED white
set_pixel_color(10, (127, 0, 255)) # 11th LED purple
time.sleep(1)

# Turn off all LEDs
set_all_pixels((0, 0, 0))