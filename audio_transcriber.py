import os
from vosk import Model, KaldiRecognizer
import pyaudio
import json
from api_communicator import VoiceflowAPI

class AudioTranscriber:
    def __init__(self):
        model_path = "./models/vosk-model-small-en-us-0.15"
        if not os.path.exists(model_path):
            raise FileNotFoundError("Speech recognition model not found.")
        
        self.model = Model(model_path)
        self.audio_interface = pyaudio.PyAudio()
        self.stream = None
        self.is_listening = False
        self.recorded_data = []
        self.create_new_recognizer()
        
        # Initialize Voiceflow API
        try:
            self.voiceflow = VoiceflowAPI()
        except ValueError as e:
            print(f"Warning: {e}")
            self.voiceflow = None

    def create_new_recognizer(self):
        self.recognizer = KaldiRecognizer(self.model, 16000)

    def start_listening(self):
        if self.stream is not None:
            return  # Already listening
            
        print("Listening started")
        self.recorded_data = []  # Clear previous recording
        
        try:
            self.stream = self.audio_interface.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=2048,
                stream_callback=None,
                start=True
            )
            self.is_listening = True
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            self.cleanup()

    def record_chunk(self):
        """Record a single chunk of audio"""
        if self.is_listening and self.stream:
            try:
                data = self.stream.read(1024, exception_on_overflow=False)
                if data:
                    self.recorded_data.append(data)
            except Exception as e:
                print(f"Error recording audio: {e}")

    def stop_listening(self):
        print("Stopping listening...")
        self.is_listening = False
        
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            except Exception as e:
                print(f"Error closing stream: {e}")

        self.process_audio()
        print("Listening stopped")

    def process_audio(self):
        if not self.recorded_data:
            print("\nNo audio to process")
            return
            
        self.create_new_recognizer()  # Fresh recognizer for each processing
        
        try:
            for data in self.recorded_data:
                self.recognizer.AcceptWaveform(data)
            
            result = json.loads(self.recognizer.FinalResult())
            if result.get('text'):
                transcription = result['text']
                print("\nTranscription:", transcription)
                
                # Send to Voiceflow if available
                if self.voiceflow:
                    response = self.voiceflow.send_transcription(transcription)
                    if response:
                        print("Voiceflow response:", json.dumps(response, indent=2))
            else:
                print("\nNo speech detected")
        except Exception as e:
            print(f"Error processing audio: {e}")
        
        self.recorded_data = []  # Clear the processed data

    def __del__(self):
        self.stop_listening()
        if self.audio_interface:
            self.audio_interface.terminate()