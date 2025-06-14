# src/recognizer_mac.py
import sounddevice as sd
import queue
import vosk
import json

class MacSpeechRecognizer:
    def __init__(self):
        self.q = queue.Queue()
        self.model = vosk.Model("model")  # or full path to your Vosk model
        self.samplerate = 16000

        # Try to use default input device or let user choose
        self.device = None  # or set this to a device index
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            device=self.device,
            channels=1,
            dtype='int16',
            callback=self.callback
        )
        self.stream.start()

    def callback(self, indata, frames, time, status):
        if status:
            print(f"⚠️ Mic status: {status}")
        self.q.put(bytes(indata))

    def listen(self):
        print("🎧 Listening...")

        rec = vosk.KaldiRecognizer(self.model, self.samplerate)
        while True:
            data = self.q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                return result.get("text", "")
