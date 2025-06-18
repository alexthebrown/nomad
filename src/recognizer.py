import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer
import os

# Adjust this if the model is located elsewhere
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../model")

# Sampling rate must match model
SAMPLE_RATE = 16000 # Check if your microphone supports this sample rate.

class SpeechRecognizer:
    def __init__(self, device_index=None):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Vosk model not found. Download and extract it to 'model/'")
        self.model = Model(MODEL_PATH)
        # Ensure the sample rate here matches the Vosk model
        self.rec = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.q = queue.Queue()
        self.device_index = device_index

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[Warning] {status}", flush=True)
        self.q.put(bytes(indata))

    def listen(self, timeout=10):
        """Capture audio for a given time and return recognized text."""
        result_text = ""  # Initialize result_text here

        try:
            with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                                   channels=1, callback=self._callback,
                                   device=self.device_index):
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
            # You might want to handle this error more gracefully

        return result_text.strip()

# Quick test
if __name__ == "__main__":
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

    recognizer = SpeechRecognizer(device_index=microphone_device_index)
    print("You said:", recognizer.listen())
