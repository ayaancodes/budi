import rumps
import audio_transcriber
import keyboard

class BuddyApp(rumps.App):
    def __init__(self):
        super(BuddyApp, self).__init__("Buddy", icon="assets/icon.png")
        self.mic_muted = False
        self.menu = ["Mute/Unmute Mic"]
        self.audio_transcriber = audio_transcriber.AudioTranscriber()

        # Register the hotkey for push-to-talk
        keyboard.add_hotkey('cmd+b', self.push_to_talk)

    @rumps.clicked("Mute/Unmute Mic")
    def toggle_mic(self, _):
        self.mic_muted = not self.mic_muted
        if self.mic_muted:
            self.audio_transcriber.stop_listening()
            rumps.alert("Microphone muted")
        else:
            rumps.alert("Microphone unmuted")

    def push_to_talk(self):
        if not self.mic_muted:
            self.audio_transcriber.start_listening()
            keyboard.wait('cmd+b', suppress=True)  # Wait for the key to be released
            self.audio_transcriber.stop_listening()

if __name__ == "__main__":
    BuddyApp().run()