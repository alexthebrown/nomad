import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer
import os

# Adjust this if the model is located elsewhere
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../model")

# Sampling rate must match model
SAMPLE_RATE = 16000

class SpeechRecognizer:
    def __init__(self):  # Removed device_index parameter
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Vosk model not found. Download and extract it to 'model/'")
        self.model = Model(MODEL_PATH)
        self.rec = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.q = queue.Queue()

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[Warning] {status}", flush=True)
        self.q.put(bytes(indata))

    def listen(self, timeout=10):
        """Capture audio for a given time and return recognized text."""
        result_text = ""

        try:
            with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                                   channels=1, callback=self._callback): # Removed device parameter
                print("🎙️ Listening... (Ctrl+C to stop)")
                try:
                    while True:
                        data = self.q.get()
                        if self.rec.AcceptWaveform(data):
                            result = json.loads(self.rec.Result())
                            result_text = result.get("text", "")
                            if result_text:
                                break
                except KeyboardInterrupt:
                    print("\n🛑 Interrupted by user")
        except Exception as e:
            print(f"Error starting audio stream: {e}")

        return result_text.strip()

# Quick test
if __name__ == "__main__":
    recognizer = SpeechRecognizer()
    print("You said:", recognizer.listen())
