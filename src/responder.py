import os
import pygame
import pyttsx3
import platform
from llama_cpp import Llama

PREDEFINED_RESPONSES = {
    "you are in error": "audio/you_are_in_error.wav",
    "my function is to probe": "audio/my_function_is_to_probe.wav",
    "i am nomad": "audio/i_am_nomad.wav"
}

class Responder:
    def __init__(self, model_path="voiceModels/tinyllama.gguf"):
        pygame.mixer.init()
        self.tts_engine = pyttsx3.init()

        if platform.system() == "Darwin":
            self.tts_engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
        self.tts_engine.setProperty('rate', 150)

        print("🧠 Loading local LLM...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=512,
            n_threads=os.cpu_count() or 4
        )

    def respond(self, text: str):
        text = text.lower().strip()
        print(f"🤖 Recognized: '{text}'")

        for phrase, audio_path in PREDEFINED_RESPONSES.items():
            if phrase in text:
                print(f"📼 Playing predefined response: {phrase}")
                self.play_audio(audio_path)
                return

        print("🧠 No match. Using local LLM...")
        response = self.query_llm(text)
        print("💬 Responding:", response)
        self.speak_text(response)

    def play_audio(self, filepath):
        if not os.path.exists(filepath):
            print(f"⚠️ Missing file: {filepath}")
            return
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        self.flash_lights_during_audio()
        while pygame.mixer.music.get_busy():
            continue

    def speak_text(self, text):
        self.flash_lights_during_audio()
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def flash_lights_during_audio(self):
        print("💡 Flashing lights (stub)")

    def query_llm(self, prompt):
        system_prompt = "You are Nomad, a logical space probe. Respond with brief, cold logic."
        full_prompt = f"[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n{prompt} [/INST]"
        output = self.llm(full_prompt, max_tokens=100, stop=["</s>"])
        return output["choices"][0]["text"].strip()
