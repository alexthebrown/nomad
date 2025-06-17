from src.audio_player import AudioPlayer
from src.matcher import match_trigger
from src.recognizer import SpeechRecognizer
from src.responder import Responder
from src.speaker import Speaker
from web.server import run_server, get_control_flags, log_event
import threading
from src.led_controller import audio_reactive_led_control

import time
import board
import neopixel
import random
import pyaudio
import numpy as np

# --- NeoPixel Configuration ---
LED_COUNT = 24  # Assuming 4 sides * 6 LEDs/side = 24 LEDs
LED_PIN = board.D18

pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)

LEDS_PER_SIDE = 6
NUM_SIDES = 4

# Define your two colors for the top two LEDs on each side
TOP_LED_COLOR_1 = (255, 0, 0)  # Example: Red
TOP_LED_COLOR_2 = (252, 244, 3)  # Example: Yellow

# --- Audio Configuration ---
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1 # Or 2 for stereo
RATE = 44100 # Adjust as needed
AUDIO_INTENSITY_THRESHOLD = 500  # Adjust as needed
MAX_AUDIO_INTENSITY = 10000 # Adjust as needed

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

def random_pattern_thread(stop_event):  # Pass stop_event to the thread
    while not stop_event.is_set():  # Check the event in the loop
        set_random_leds((0, 255, 0))
        pixels.show()
        time.sleep(random.uniform(0.1, 0.5))
    log_event("Random pattern thread stopping gracefully.") # Log shutdown

def audio_reactive_led_control(stop_event): # Pass stop_event to the thread
    p = pyaudio.PyAudio()

    try:
        # Find the device index of your microphone or loopback capture device
        input_device_index = None # Replace with the actual index if needed

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=input_device_index) # Specify the device if needed

        while not stop_event.is_set():  # Check the event in the loop
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                intensity = np.sqrt(np.mean(np.square(audio_data)))

                brightness = 0.0
                if intensity > AUDIO_INTENSITY_THRESHOLD:
                     brightness = min(1.0, (intensity - AUDIO_INTENSITY_THRESHOLD) / (MAX_AUDIO_INTENSITY - AUDIO_INTENSITY_THRESHOLD))

                for side in range(NUM_SIDES):
                    start_index = side * LEDS_PER_SIDE
                    pixels[start_index] = tuple(int(c * brightness) for c in TOP_LED_COLOR_1)
                    pixels[start_index + 1] = tuple(int(c * brightness) for c in TOP_LED_COLOR_2)

                pixels.show()

            except IOError as e:
                print(f"Error reading audio stream: {e}")

    except Exception as e:
        print(f"Error in LED control thread: {e}")

    finally:
        pixels.fill((0, 0, 0)) # Turn off all LEDs
        pixels.show()
        if 'stream' in locals() and stream.is_active():
            stream.stop_stream()
            stream.close()
        p.terminate()
        log_event("Audio reactive LED thread stopping gracefully.") # Log shutdown


if __name__ == "__main__":
    # Create the stop event
    stop_event = threading.Event()

    recognizer = SpeechRecognizer()
    responder = Responder()
    speaker = Speaker()
    audioPlayer = AudioPlayer()

    # Start the LED control in a separate thread, passing the stop_event
    led_thread = threading.Thread(target=audio_reactive_led_control, args=(stop_event,), daemon=True)
    led_thread.start()

    # Verify if the thread started successfully
    if led_thread.is_alive():
        log_event("led_thread started successfully")
    else:
        log_event("led_thread failed to start")

    log_event("led_thread active")

    # Start the random pattern thread, passing the stop_event
    random_thread = threading.Thread(target=random_pattern_thread, args=(stop_event,), daemon=True)
    random_thread.start()
    log_event("random_thread active")

    # Start web server (assumes this is a blocking call)
    try:
        run_server()
        control = get_control_flags()

        log_event("🎤 Nomad is now listening...")

        WAKE_WORD = "nomad"

        while True:
            if control["shutdown"]:
                log_event("🔻 Nomad is shutting down via control panel.")
                break

            if control["reset"]:
                log_event("🔄 Reset command received. (Handled here if needed)")
                control["reset"] = False  # Clear flag
                # Add actual reset behavior here

            text = recognizer.listen()
            if not text:
                continue

            log_event(f"🗣 Heard: {text}")

            if WAKE_WORD not in text.lower():
                continue

            if "shutdown" in text.lower():
                log_event("🛑 Nomad received voice shutdown command.")
                break

            path = match_trigger(text)
            if path:
                log_event(f"🎬 Playing clip for: {text}")
                audioPlayer.play(path)
            else:
                reply = responder.get_response(text)
                log_event(f"🤖 Nomad says: {reply}")
                speaker.speak(reply)

    except KeyboardInterrupt:
        log_event("KeyboardInterrupt received. Signaling threads to stop.")
        stop_event.set() # Signal the threads to stop

    finally:
        # Join the threads to wait for them to finish their cleanup
        led_thread.join()
        random_thread.join()
        log_event("All threads have stopped.")
