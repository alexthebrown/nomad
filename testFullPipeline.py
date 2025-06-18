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

# ... (rest of your configurations and helper functions) ...

def audio_reactive_led_control(stop_event):
    # ... (audio processing and LED control logic) ...
    pass # Example placeholder

def random_pattern_thread(stop_event):
    # ... (random pattern logic) ...
    pass # Example placeholder


if __name__ == "__main__":
    # Create the stop event
    stop_event = threading.Event()

    recognizer = SpeechRecognizer()
    responder = Responder()
    speaker = Speaker()
    audioPlayer = AudioPlayer()

    # Start the LED control thread
    led_thread = threading.Thread(target=audio_reactive_led_control, args=(stop_event,), daemon=True)
    led_thread.start()

    # Start the random pattern thread
    random_thread = threading.Thread(target=random_pattern_thread, args=(stop_event,), daemon=True)
    random_thread.start()

    if led_thread.is_alive:
        log_event("Reactive Audio Thread Active")
    else:
        log_event("Reative Audio Thread Not Active")

    if random_thread.is_alive:
        log_event("Random LED Thread Active")
    else:
        log_event("Random LED Thread Not Active")

    # Start web server (assumes this is a blocking call)
    try:
        run_server()
        control = get_control_flags()

        log_event("🎤 Nomad is now listening...")

        WAKE_WORD = "nomad"

        # Wrap the main loop in a try...except block
        try:
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
            log_event("KeyboardInterrupt received in main loop. Signaling threads to stop.")
            stop_event.set() # Signal the threads to stop

    except KeyboardInterrupt:
        # This outer block catches the initial KeyboardInterrupt when you press Ctrl+C
        log_event("KeyboardInterrupt received. Signaling threads to stop.")
        stop_event.set() # Signal the threads to stop

    finally:
        # Join the threads to wait for them to finish their cleanup
        led_thread.join()
        random_thread.join()
        log_event("All threads have stopped.")
