from src.audio_player import AudioPlayer
from src.matcher import match_trigger
from src.recognizer_mac import MacSpeechRecognizer
from src.responder import Responder
from src.speaker import Speaker
from web.server import run_server, get_control_flags, log_event

recognizer = MacSpeechRecognizer()
responder = Responder()
speaker = Speaker()
audioPlayer = AudioPlayer()

# Start web server
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
