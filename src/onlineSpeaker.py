# src/speaker.py
from gtts import gTTS
import os
import tempfile
import pygame

class Speaker:
    def __init__(self):
        pygame.mixer.init()

    def speak(self, text):
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as f:
            tts.save(f.name)
            pygame.mixer.music.load(f.name)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
