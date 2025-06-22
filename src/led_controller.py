import time
import board
import neopixel
import random
import threading # Ensure threading is imported

class LED_CONTROLLER:
    def __init__(self, pixel_pin, led_count, brightness=0.2, pixel_order=neopixel.GRB):
        # Initialize NeoPixel strip
        self.pixel_pin = pixel_pin
        self.led_count = led_count
        self.brightness = brightness
        self.pixel_order = pixel_order
        self.pixels = neopixel.NeoPixel(
            self.pixel_pin, self.led_count, brightness=self.brightness, auto_write=False, pixel_order=self.pixel_order
        )

        # Define the sequence of LED types for the 24 LEDs (index 0 to 23)
        # This replaces the old LEDS_PER_SIDE and NUM_SIDES for addressing
        self.LED_TYPE_SEQUENCE = [
            1, 2, 4, 3, 5, 6,
            5, 6, 4, 3, 2, 1,
            1, 2, 4, 3, 5, 6,
            5, 6, 4, 3, 2, 1
        ]
        
        # Ensure LED_COUNT matches the length of LED_TYPE_SEQUENCE
        if len(self.LED_TYPE_SEQUENCE) != self.led_count:
            raise ValueError(f"LED_TYPE_SEQUENCE length ({len(self.LED_TYPE_SEQUENCE)}) must match led_count ({self.led_count})")

        # Define base colors for each LED type
        # You can adjust these RGB values as needed
        self.TYPE_COLORS = {
            1: (255, 0, 0),    # Top Red
            2: (252, 244, 3),  # Top Yellow
            3: (0, 255, 0),    # Green #1
            4: (0, 200, 0),    # Green #2 (slightly darker green)
            5: (0, 150, 0),    # Green #3 (even darker green)
            6: (0, 100, 0)     # Green #4 (darkest green)
        }

        # Define top LED colors based on type definitions
        self.TOP_LED_COLOR_1 = self.TYPE_COLORS[1]
        self.TOP_LED_COLOR_2 = self.TYPE_COLORS[2]

        # Calculate middle brightness colors for top LEDs
        self.MIDDLE_BRIGHTNESS_FACTOR = 0.2
        self.MIDDLE_COLOR_1 = tuple(int(c * self.MIDDLE_BRIGHTNESS_FACTOR) for c in self.TOP_LED_COLOR_1)
        self.MIDDLE_COLOR_2 = tuple(int(c * self.MIDDLE_BRIGHTNESS_FACTOR) for c in self.TOP_LED_COLOR_2)
        
        # Define flash timings
        self.FLASH_ON_TIME = 0.2
        self.FLASH_OFF_TIME = 0.01

    def breathe_color(self, color, duration=2.0, steps=50):
        """Generator function to yield colors for a breathing effect."""
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

    def set_top_leds(self, color1, color2):
        """
        Sets the color of LEDs identified as type 1 (red) and type 2 (yellow)
        in the LED_TYPE_SEQUENCE.
        """
        for i, led_type in enumerate(self.LED_TYPE_SEQUENCE):
            if led_type == 1:
                self.pixels[i] = color1
            elif led_type == 2:
                self.pixels[i] = color2
            # LEDs of other types (3-6) are not modified by this function
        self.pixels.show()

    def set_random_leds(self, on_color):
        """
        Randomly turns LEDs of types 3, 4, 5, and 6 on or off.
        LEDs of types 1 and 2 are left untouched.
        """
        for i, led_type in enumerate(self.LED_TYPE_SEQUENCE):
            if led_type in [3, 4, 5, 6]:
                if random.random() < 0.5: # 50% chance to turn on
                    self.pixels[i] = on_color
                else:
                    self.pixels[i] = (0, 0, 0) # Turn off
            # LEDs of types 1 and 2 are intentionally ignored by this function
        # self.pixels.show() is called by the random_pattern_thread, not here

    def clear_all_leds(self):
        """Sets all LEDs on the strip to off (black)."""
        self.pixels.fill((0, 0, 0))
        self.pixels.show()

    def random_pattern_thread(self, stop_event):
        """
        Thread for a random on/off pattern on LEDs of types 3-6.
        This thread is responsible for calling .show() for its updates.
        """
        print("Random pattern thread starting.")
        while not stop_event.is_set():
            # Pass a green color to set_random_leds for the 'on' state
            self.set_random_leds(self.TYPE_COLORS[3]) # Using TYPE_COLORS[3] as a generic green for randoms
            self.pixels.show() # Update the physical LEDs after setting the random pattern
            time.sleep(random.uniform(0.1, 0.5)) # Vary the delay
        self.clear_all_leds() # Ensure all LEDs are off at thread exit
        print("Random pattern thread stopping gracefully.")

    def audio_reactive_led_control(self, stop_event, talk_event):
        """
        Controls top LEDs (type 1 and 2) based on talk_event:
        rapid flashing when talking, solid middle brightness when not.
        """
        print("Audio reactive LED control thread starting.")
        self.clear_all_leds() # Start with all LEDs off
        
        last_talk_state = False # Track the previous state to avoid redundant updates

        while not stop_event.is_set():
            current_talk_state = talk_event.is_set()
            
            if current_talk_state:
                # Rapidly flash when talk_event is set
                self.set_top_leds(self.TOP_LED_COLOR_1, self.TOP_LED_COLOR_2) # Full brightness flash ON
                time.sleep(self.FLASH_ON_TIME)
                if stop_event.is_set(): break # Check if stop requested during sleep

                self.set_top_leds((0, 0, 0), (0, 0, 0)) # Turn off for flash OFF
                time.sleep(self.FLASH_OFF_TIME)
                if stop_event.is_set(): break # Check if stop requested during sleep
            
            else:
                # Solid middle brightness when not talking
                # Only update if the state has changed from talking to not talking
                if last_talk_state or (not last_talk_state and not current_talk_state):
                    # Set type 1 and 2 LEDs to middle brightness
                    self.set_top_leds(self.MIDDLE_COLOR_1, self.MIDDLE_COLOR_2)
                time.sleep(0.1) # A longer sleep is fine when solid

            last_talk_state = current_talk_state # Update last state

        # Cleanup: Ensure all LEDs are off when the loop exits
        self.clear_all_leds()
        print("Audio reactive LED control thread stopping gracefully.")

# --- Example Usage (Main execution block for demonstration) ---
if __name__ == '__main__':
    # Configuration for your NeoPixel strip
    PIXEL_PIN = board.D18 # GPIO pin, e.g., board.D18 for physical pin 12
    LED_COUNT = 24       # Total number of LEDs on your strip

    # Create the LED controller instance
    controller = LED_CONTROLLER(PIXEL_PIN, LED_COUNT)

    # Create threading events for control
    stop_all_event = threading.Event() # For stopping all LED threads
    talk_event = threading.Event()      # For signaling talking state

    # Start the random pattern thread for types 3-6 LEDs
    random_thread = threading.Thread(target=controller.random_pattern_thread, args=(stop_all_event,))
    random_thread.start()

    # Start the audio reactive thread for type 1-2 LEDs
    audio_reactive_thread = threading.Thread(target=controller.audio_reactive_led_control, args=(stop_all_event, talk_event,))
    audio_reactive_thread.start()

    print("\n--- LED Control Demo Started ---")
    print("Top LEDs (Type 1, 2) initially solid at middle brightness.")
    print("Other LEDs (Type 3-6) will show random patterns.")
    print("Press 'Enter' to toggle 'talking' state. Press Ctrl+C to exit.")

    try:
        while True:
            input() # Wait for user input to toggle state
            if talk_event.is_set():
                talk_event.clear()
                print("\n--- Not Talking: Top LEDs solid middle brightness ---")
            else:
                talk_event.set()
                print("\n--- TALKING: Top LEDs rapidly flashing ---")

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Signaling all threads to stop...")
    finally:
        stop_all_event.set() # Signal all threads to stop
        random_thread.join() # Wait for random thread to finish
        audio_reactive_thread.join() # Wait for audio reactive thread to finish
        controller.clear_all_leds() # Ensure all LEDs are off on final exit
        print("All LED threads stopped. Program finished.")

