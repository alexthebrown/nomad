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
CHANNELS = 1
RATE = 44100

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

# Function to find the audio device index
def find_input_device_index():
    p = pyaudio.PyAudio()
    try:
        device_count = p.get_device_count()
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            print(f"Device {i}: {device_info['name']}")
            if device_info['maxInputChannels'] > 0:
                # You might need to adjust this condition based on your microphone's name or characteristics
                if "your_microphone_name" in device_info['name'].lower():
                    return i
    finally:
        p.terminate()
    return None

# Get the audio device index
input_device_index = find_input_device_index()
if input_device_index is None:
    print("Error: Audio input device not found.")
    # Handle the error or exit the script appropriately
    exit()

def audio_reactive_led_control():
    p = pyaudio.PyAudio()

    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        # Create the random pattern thread
        random_thread = threading.Thread(target=random_pattern_thread, daemon=True)
        random_thread.start()

        while True:
            # Read audio data
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)

            # Calculate audio intensity (e.g., RMS)
            # You might need to experiment with different analysis methods
            intensity = np.sqrt(np.mean(np.square(audio_data)))

            # Map intensity to brightness (0.0 to 1.0)
            # Adjust the mapping function as needed
            brightness = min(1.0, intensity / 32768.0) # Assuming 16-bit audio

            # Set the brightness of the top LEDs based on audio intensity
            for side in range(NUM_SIDES):
                start_index = side * LEDS_PER_SIDE
                pixels[start_index] = (TOP_LED_COLOR_1[0] * brightness, TOP_LED_COLOR_1[1] * brightness, TOP_LED_COLOR_1[2] * brightness)
                pixels[start_index + 1] = (TOP_LED_COLOR_2[0] * brightness, TOP_LED_COLOR_2[1] * brightness, TOP_LED_COLOR_2[2] * brightness)

            pixels.show()

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
    audio_reactive_led_control()

