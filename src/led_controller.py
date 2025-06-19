import time
import board
import neopixel
import random
import threading

class LED_CONTROLLER:
    def __init__(self, pixel_pin, led_count, brightness=0.2, pixel_order=neopixel.GRB):
        # Initialize instance attributes
        self.pixel_pin = pixel_pin
        self.led_count = led_count
        self.brightness = brightness
        self.pixel_order = pixel_order
        self.pixels = neopixel.NeoPixel(
            self.pixel_pin, self.led_count, brightness=self.brightness, auto_write=False, pixel_order=self.pixel_order
        )

        

        self.LEDS_PER_SIDE = 6  # Assuming 4 sides * 6 LEDs/side = 24 LEDs total
        self.NUM_SIDES = self.led_count // self.LEDS_PER_SIDE

        # Define your two colors for the top two LEDs on each side (as instance attributes)
        self.TOP_LED_COLOR_1 = (255, 0, 0)  # Example: Red
        self.TOP_LED_COLOR_2 = (252, 244, 3)  # Example: Yellow

        self.MIDDLE_BRIGHTNESS_FACTOR = 0.5
        self.MIDDLE_COLOR_1 = tuple(int(c * self.MIDDLE_BRIGHTNESS_FACTOR) for c in self.TOP_LED_COLOR_1)
        self.MIDDLE_COLOR_2 = tuple(int(c * self.MIDDLE_BRIGHTNESS_FACTOR) for c in self.TOP_LED_COLOR_2)
        

        self.FLASH_ON_TIME = 0.2
        self.FLASH_OFF_TIME = 0.05

    def breathe_color(self, color, duration=2.0, steps=50): # Add self
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

    def set_top_leds(self, color1, color2): # Add self
        for side in range(self.NUM_SIDES): # Use self.NUM_SIDES
            start_index = side * self.LEDS_PER_SIDE # Use self.LEDS_PER_SIDE
            self.pixels[start_index] = color1 # Use self.pixels
            self.pixels[start_index + 1] = color2 # Use self.pixels
            self.pixels.show()


    def set_random_leds(self, color): # Add self
        for i in range(2, self.LEDS_PER_SIDE): # Use self.LEDS_PER_SIDE
            if random.random() < 0.5:
                for side in range(self.NUM_SIDES): # Use self.NUM_SIDES
                    self.pixels[side * self.LEDS_PER_SIDE + i] = color # Use self.pixels and self.LEDS_PER_SIDE
            else:
                for side in range(self.NUM_SIDES): # Use self.NUM_SIDES
                    self.pixels[side * self.LEDS_PER_SIDE + i] = (0, 0, 0) # Use self.pixels and self.LEDS_PER_SIDE

    def random_pattern_thread(self, stop_event): # Add self and stop_event
        while not stop_event.is_set():  # Check the event in the loop
            self.set_random_leds((0, 255, 0)) # Call with self.
            self.pixels.show() # Use self.pixels
            time.sleep(random.uniform(0.1, 0.5))
        print("Random pattern thread stopping gracefully.") # Log shutdown

    def audio_reactive_led_control(self, stop_event, talk_event): # Add self and stop_event
        # Removed audio sampling and replaced with breathing effect
        # The while loop will now handle the breathing pattern

        last_talk_state = False
        while not stop_event.is_set(): 
            current_talk_state = talk_event.is_set() # Check the event in the loop
            
            if current_talk_state:
                self.set_top_leds(self.TOP_LED_COLOR_1, self.TOP_LED_COLOR_2)
                time.sleep(self.FLASH_ON_TIME)
                if stop_event.is_set(): break

                self.set_top_leds((0,0,0), (0,0,0))
                time.sleep(self.FLASH_OFF_TIME)
                if stop_event.is_set(): break
            
            else:
                self.set_top_leds(self.MIDDLE_COLOR_1, self.MIDDLE_COLOR_2)
                time.sleep(0.1)

            current_talk_state = current_talk_state
        
            
        # Cleanup is handled in the finally block below
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
        print("Audio reactive LED thread stopping gracefully.") # Log shutdown

