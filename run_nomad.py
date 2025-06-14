from src.audio_player import AudioPlayer
from src.matcher import match_trigger
from src.recognizer_mac import MacSpeechRecognizer
from src.recognizer import SpeechRecognizer
from src.responder import Responder
from src.speaker import Speaker
from web.server import run_server, get_control_flags, log_event

recognizer = SpeechRecognizer()
responder = Responder()
speaker = Speaker()
audioPlayer = AudioPlayer()

# Start Web Server
run_server()
log_event("Web Server Running")