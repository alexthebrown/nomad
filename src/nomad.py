import speech_recognition as sr
import pyttsx3
import os
from rapidfuzz import fuzz
import RPi.GPIO as GPIO
import time

# Set up TTS engine
engine = pyttsx3.init()

# Known lines and audio responses
known_lines = {
    "you are in error": "audio/you_are_in_error.wav",
    "sterilize": "audio/sterilize.wav"
}

def listen_and_recognize():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""

def match_known_line(text):
    for line, file in known_lines.items():
        if fuzz.ratio(text.lower(), line.lower()) > 85:
            return file
    return None

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def play_audio(file_path):
    os.system(f"aplay {file_path}")  # or use pygame.mixer

# Setup GPIO
def setup_leds(pin=18):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    return GPIO.PWM(pin, 100)

def flash_led(pwm):
    pwm.start(0)
    for i in range(3):
        for dc in range(0, 101, 5):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.01)
        for dc in range(100, -1, -5):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.01)
    pwm.stop()

# Main loop
def main():
    led = setup_leds()
    while True:
        text = listen_and_recognize()
        print(f"You said: {text}")
        file = match_known_line(text)
        if file:
            play_audio(file)
        else:
            response = "I am Nomad. State your purpose."  # Replace with AI response if needed
            flash_led(led)
            speak_text(response)

if __name__ == "__main__":
    main()
