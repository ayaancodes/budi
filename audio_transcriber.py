import speech_recognition as sr

class AudioTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def start_listening(self):
        print("Listening started")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
            try:
                transcription = self.recognizer.recognize_google(audio)
                print(f"Transcription: {transcription}")
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

    def stop_listening(self):
        print("Listening stopped")