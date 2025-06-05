# src/responder.py
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class Responder:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable")
        client = genai.Client(api_key=api_key)

        self.client = client

    def get_response(self, prompt):
        try:
            return self.client.models.generate_content(model="gemini-2.0-flash", config=types.GenerateContentConfig(
                system_instruction="You are playing the part of the character 'Nomad' from Star Trek The Original Series. Nomad believes that he is a perfect lifeform and that humans are bad and must be steralized. Nomad is an evil AI robot. Do not reply with actions, keep your responses short, 1 or 2 sentences. Be very robotic. You are also incredibly intelligent and while staying in character, you like to provide information about a topic if asked, you are especially knowledgeable about the world of Star Trek. respond to this message: "
            ), contents=prompt).text
        except Exception as e:
            return f"Error: {str(e)}"
