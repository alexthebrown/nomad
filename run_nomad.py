from src.audio_player import AudioPlayer
from src.matcher import match_trigger
from src.recognizer_mac import MacSpeechRecognizer
from src.recognizer import SpeechRecognizer
from src.responder import Responder
from src.speaker import Speaker
from web.server import run_server, get_control_flags, log_event
import threading
from src.led_control import audio_reactive_led_control

recognizer = SpeechRecognizer()
responder = Responder()
speaker = Speaker()
audioPlayer = AudioPlayer()

# Start Web Server
run_server()
log_event("Web Server Running")

led_thread = threading.Thread(target=audio_reactive_led_control, daemon=True)
led_thread.start()