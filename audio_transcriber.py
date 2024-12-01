import wave
import os
from vosk import Model, KaldiRecognizer
import pyaudio

class AudioTranscriber:
    def __init__(self):
        # Set the path to the Vosk model directory
        model_path = "./models/vosk-model-small-en-us-0.15"
        if not os.path.exists(model_path):
            raise FileNotFoundError("Speech recognition model not found.")
        
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.audio_interface = pyaudio.PyAudio()
        self.stream = None

    def start_listening(self):
        print("Listening started")
        self.stream = self.audio_interface.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        self.stream.start_stream()

        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                result = self.recognizer.Result()
                print(f"Transcription: {result}")

    def stop_listening(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        print("Listening stopped")