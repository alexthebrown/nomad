from src.audio_player import AudioPlayer
from src.matcher import match_trigger
from src.recognizer import SpeechRecognizer
from src.responder import Responder
from src.speaker import Speaker
from web.server import WebServer
import threading
from src.led_controller import LED_CONTROLLER
from flask import Flask, request, jsonify, render_template_string
import threading

import time
import board
import neopixel
import random
import pyaudio
import numpy as np

control_state = {
        "reset": False,
        "shutdown": False,
        "logs": ["Initial log entry"]
    }

def nomad_main_thread(stop_event, talk_event):
    # WAKE_WORD = 'nomad'
    WAKE_WORD = ''

    print("🎤 Nomad is now listening...")
    try:
        while True:
            text = recognizer.listen()
            if not text:
                continue

            print(f"Heard: {text}")

            if WAKE_WORD not in text.lower():
                continue

            if "shut down" in text.lower():
                print("Nomad received voice shutdown command.")
                break

            path = match_trigger(text)
            if path:
                talk_event.set()
                print(f"Playing clip for: {text}")
                audioPlayer.play(path)
            else:
                pass
                # reply = responder.get_response(text)
                # newPath = match_trigger(reply)
                # if newPath:
                #     talk_event.set()
                #     print(f"Playing clip for: {text}")
                #     audioPlayer.play(newPath)
                # else:
                #     talk_event.set()
                #     print(f"Nomad says: {reply}")
                #     speaker.speak(reply)
            talk_event.clear()

    except KeyboardInterrupt:
        print("KeyboardInterrupt received in main loop. Signaling threads to stop.")
        stop_event.set()




def nomad_web_server_thread(stop_event):
    try:
        webServer = WebServer(control_state, stop_event)
        webServer.run()
    except Exception as e:
        print(f"Error in nomad_web_server_thread: {e}")
        stop_event.set()

if __name__ == "__main__":
    stop_event = threading.Event()
    talk_event = threading.Event()
    #Instantiate components
    recognizer = SpeechRecognizer()
    responder = Responder()
    speaker = Speaker()
    audioPlayer = AudioPlayer()

    led_controller = LED_CONTROLLER(board.D18, 24)

    # Start the LED control thread
    led_thread = threading.Thread(target=led_controller.audio_reactive_led_control, args=(stop_event,talk_event,), daemon=True)
    led_thread.start()

    # Start the random pattern thread
    random_thread = threading.Thread(target=led_controller.random_pattern_thread, args=(stop_event,), daemon=True)
    random_thread.start()

    # Start Nomad Call And Response thread
    call_response_thread = threading.Thread(target=nomad_main_thread, args=(stop_event, talk_event,), daemon=True)
    call_response_thread.start()

    # Start Nomad Web Server thread
    web_server_thread = threading.Thread(target=nomad_web_server_thread, args=(stop_event,), daemon=True)
    web_server_thread.start()

    if led_thread.is_alive:
        print("Reactive Audio Thread Active")
    else:
        print("Reative Audio Thread Not Active")

    if random_thread.is_alive:
        print("Random LED Thread Active")
    else:
        print("Random LED Thread Not Active")

    if call_response_thread.is_alive:
        print("Nomad Thread Active")
    else:
        print("Nomad Thread Not Active")

    if web_server_thread.is_alive:
        print("Nomad Web Server Thread Active")
    else:
        print("Monad Web Server Threat Not Active")

    try:
        while True:
            pass

    except KeyboardInterrupt:
        # This outer block catches the initial KeyboardInterrupt when you press Ctrl+C
        print("KeyboardInterrupt received. Signaling threads to stop.")
        stop_event.set() # Signal the threads to stop

    finally:
        led_thread.join()
        random_thread.join()
        call_response_thread.join()
        print("All threads have stopped.")