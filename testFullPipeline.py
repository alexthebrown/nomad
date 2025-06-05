# testFullPipeline.py
from src.audio_player import AudioPlayer
from src.matcher import match_trigger
from src.recognizer_mac import MacSpeechRecognizer  # or recognizer_pi
from src.responder import Responder
from src.speaker import Speaker

recognizer = MacSpeechRecognizer()
responder = Responder()
speaker = Speaker()
audioPlayer = AudioPlayer()

print("🎤 Say something to Nomad...")

while True:
    text = recognizer.listen()
    print(f"You said: {text}")

    if not text:
        continue

    if "shutdown" in text.lower():
        print("Shutting down Nomad.")
        break

    path = match_trigger(text)
    if path:
        print(f"🎬 Playing clip for match: {text}")
        audioPlayer.play(path)
    else:
        reply = responder.get_response(text)
        print(f"Nomad: {reply}")
        speaker.speak(reply)
