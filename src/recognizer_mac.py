import pyaudio
import json
from vosk import Model, KaldiRecognizer
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../model")
SAMPLE_RATE = 16000
CHUNK = 4096

class MacSpeechRecognizer:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Vosk model not found. Please download and extract it to 'model/'")

        self.model = Model(MODEL_PATH)
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.p = pyaudio.PyAudio()

    def listen(self, timeout=10):
        print("🎤 Listening on macOS (press Ctrl+C to interrupt)...")

        stream = self.p.open(format=pyaudio.paInt16,
                             channels=1,
                             rate=SAMPLE_RATE,
                             input=True,
                             frames_per_buffer=CHUNK)

        stream.start_stream()

        result_text = ""

        try:
            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    result_text = result.get("text", "")
                    if result_text:
                        break
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user.")
        finally:
            stream.stop_stream()
            stream.close()
            self.p.terminate()

        return result_text.strip()

# Test run
if __name__ == "__main__":
    sr = MacSpeechRecognizer()
    text = sr.listen()
    print("You said:", text)
