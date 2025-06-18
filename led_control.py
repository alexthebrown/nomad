import time
import board
import neopixel
import random
import threading
import pyaudio
import numpy as np

LED_COUNT = 24  # Assuming 4 sides * 6 LEDs/side = 24 LEDs
LED_PIN = board.D18

pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)

LEDS_PER_SIDE = 6
NUM_SIDES = 4

# Define your two colors for the top two LEDs on each side
TOP_LED_COLOR_1 = (255, 0, 0)  # Example: Red
TOP_LED_COLOR_2 = (252, 244, 3)  # Example: Yellow

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1 # Or 2 for stereo
RATE = 44100 # Adjust as needed
AUDIO_INTENSITY_THRESHOLD = 500  # Adjust as needed
MAX_AUDIO_INTENSITY = 10000 # Adjust as needed

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
        set_random_leds((0, 255, 0))
        pixels.show()
        time.sleep(random.uniform(0.1, 0.5))

def audio_reactive_led_control():
    p = pyaudio.PyAudio()

    try:
        # Find the device index of your microphone
        # You'll need to figure this out by examining the output of `arecord -l`
        # and potentially specifying the device index in the open() call
        input_device_index = 3 # Replace with the actual index if needed

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=input_device_index) # Specify the device if needed

        # Create the random pattern thread
        random_thread = threading.Thread(target=random_pattern_thread, daemon=True)
        random_thread.start()

        while True:
            try:
                # Read audio data
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)

                # Calculate audio intensity (e.g., RMS)
                intensity = np.sqrt(np.mean(np.square(audio_data)))

                # Map intensity to brightness (0.0 to 1.0)
                brightness = 0.0
                if intensity > AUDIO_INTENSITY_THRESHOLD:
                     brightness = min(1.0, (intensity - AUDIO_INTENSITY_THRESHOLD) / (MAX_AUDIO_INTENSITY - AUDIO_INTENSITY_THRESHOLD))

                # Set the brightness of the top LEDs based on audio intensity
                for side in range(NUM_SIDES):
                    start_index = side * LEDS_PER_SIDE
                    pixels[start_index] = tuple(int(c * brightness) for c in TOP_LED_COLOR_1)
                    pixels[start_index + 1] = tuple(int(c * brightness) for c in TOP_LED_COLOR_2)

                pixels.show()

            except IOError as e:
                print(f"Error reading audio stream: {e}")
                # You might want to add error handling or restart the stream here

    except KeyboardInterrupt:
        pass # Handle exit

    finally:
        # Clean up
        stream.stop_stream()
        stream.close()
        p.terminate()
        pixels.fill((0, 0, 0))
        pixels.show()


if __name__ == "__main__":
    # You can call this function from your main script
    audio_reactive_led_control()