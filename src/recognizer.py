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
    def __init__(self):
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

        # --- Specify your microphone input device index here ---
        # Find the device index using the PyAudio device listing code:
        # import pyaudio
        # p = pyaudio.PyAudio()
        # for i in range(p.get_device_count()):
        #     dev = p.get_device_info_by_index(i)
        #     print(f"Device {i}: {dev['name']}")
        # p.terminate()
        # Look for your microphone in the list and note its index.
        # Example: If your microphone is device 1
        microphone_device_index = 1 # Replace with the actual index of your microphone

        try:
            with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                                   channels=1, callback=self._callback,
                                   device=microphone_device_index): # Specify the input device
                print("🎙️ Listening... (Ctrl+C to stop)")
                result_text = ""
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
            # You might want to handle this error more gracefully

        return result_text.strip()

# Quick test
if __name__ == "__main__":
    recognizer = SpeechRecognizer()
    print("You said:", recognizer.listen())
