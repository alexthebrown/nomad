import time
import board
import neopixel
import random
import threading
import pyaudio
import numpy as np

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

        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.AUDIO_DEVICE_INDEX = 0

        self.MIN_VOLUME = 500
        self.MAX_VOLUME = 5000
        self.BRIGHTNESS_SCALE = 0.8

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

    def find_loopback_device(self):
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')

        target_card_index = 2
        target_device_index = 0

        for i in range(0, num_devices):
            if(p.get_device_info_by_host_apo_device_index(0, i).get('maxInputChannels')) > 0:
                device_name = p.get_device_info_by_host_api_device_index(0, i).get('name')
                print(f"Checking device {i}: {device_name}")

                if f"hw:{target_card_index},{target_device_index}" in device_name or "Loopback" in device_name:
                    print(f"Found Loopback device at index: {i} ({device_name})")
                    p.terminate()
                    return i
        p.terminate()
        return -1 # Device not found
    
    def calculate_rms(self, data):
        # Convert bytes to numpy array of shorts
        np_data = np.frombuffer(data, dtype=np.int16)
        # Calculate RMS
        rms = np.sqrt(np.mean(np_data**2))
        return rms

    # def audio_reactive_led_control(self, stop_event): # Add self and stop_event
    #     # Removed audio sampling and replaced with breathing effect
    #     # The while loop will now handle the breathing pattern

    #     breathe_gen1 = self.breathe_color(self.TOP_LED_COLOR_1) # Call with self.
    #     breathe_gen2 = self.breathe_color(self.TOP_LED_COLOR_2) # Call with self.

    #     while not stop_event.is_set():  # Check the event in the loop
    #         try:
    #             # Get the next color from each generator
    #             breathed_color1 = next(breathe_gen1)
    #             breathed_color2 = next(breathe_gen2)

    #             # Set the top LEDs with the breathing colors
    #             self.set_top_leds(breathed_color1, breathed_color2) # Call with self.
    #             self.pixels.show() # Use self.pixels
    #             time.sleep(0.04)

    #         except StopIteration:
    #             # If a generator is exhausted, reset it
    #             breathe_gen1 = self.breathe_color(self.TOP_LED_COLOR_1) # Call with self.
    #             breathe_gen2 = self.breathe_color(self.TOP_LED_COLOR_2) # Call with self.

    #     # Cleanup is handled in the finally block below
    #     self.pixels.fill((0, 0, 0))
    #     self.pixels.show()
    #     print("Audio reactive LED thread stopping gracefully.") # Log shutdown

    def audio_reactive_led_control(self, stop_event):
        self.AUDIO_DEVICE_INDEX = self.find_lopback_device()
        if self.AUDIO_DEVICE_INDEX == -1:
            print("Error: Loopback device (card 2, device 0) not found. Exiting audio reactive control.")
            return
        
        p = pyaudio.PyAudio()
        stream = None
        try:
            stream = p.open(format=self.FORMAT,
                            channels=self.CHANNELS,
                            rate=self.RATE,
                            input=True,
                            frames_per_buffer=self.CHUNK,
                            input_device_index=self.AUDIO_DEVICE_INDEX)
            print("Audio stream opened successfully for reactive LED control.")

            while not stop_event.is_set():
                try:
                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                    rms = self.calculate_rms(data)

                    # Normalize RMS to a 0-1 scale
                    normalized_rms = max(0, min(1, (rms - self.MIN_VOLUME) / (self.MAX_VOLUME - self.MIN_VOLUME)))

                    # Apply brightness scaling
                    brightness = normalized_rms * self.BRIGHTNESS_SCALE

                    # Map brightness to color. You can experiment with this.
                    # For a simple reactive effect, let's just adjust the brightness
                    # of your predefined colors.

                    # Interpolate colors based on brightness (optional, can be more complex)
                    # For simplicity, let's just make them brighter/dimmer
                    color1_r = int(self.TOP_LED_COLOR_1[0] * brightness)
                    color1_g = int(self.TOP_LED_COLOR_1[1] * brightness)
                    color1_b = int(self.TOP_LED_COLOR_1[2] * brightness)
                    reactive_color1 = (color1_r, color1_g, color1_b)

                    color2_r = int(self.TOP_LED_COLOR_2[0] * brightness)
                    color2_g = int(self.TOP_LED_COLOR_2[1] * brightness)
                    color2_b = int(self.TOP_LED_COLOR_2[2] * brightness)
                    reactive_color2 = (color2_r, color2_g, color2_b)

                    self.set_top_leds(reactive_color1, reactive_color2)
                    # Uncomment the following line if you're using neopixel directly
                    # self.pixels.show()

                    # Introduce a small delay to prevent excessive CPU usage, but keep it responsive
                    time.sleep(0.01)

                except IOError as e:
                    print(f"Audio stream error: {e}. Attempting to re-open stream.")
                    if stream:
                        stream.stop_stream()
                        stream.close()
                    stream = p.open(format=self.FORMAT,
                                    channels=self.CHANNELS,
                                    rate=self.RATE,
                                    input=True,
                                    frames_per_buffer=self.CHUNK,
                                    input_device_index=self.AUDIO_DEVICE_INDEX)
                except Exception as e:
                    print(f"An unexpected error occurred in audio processing: {e}")
                    time.sleep(0.1) # Prevent busy loop on persistent error

        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            p.terminate()
            print("Audio reactive LED control stopped.")
