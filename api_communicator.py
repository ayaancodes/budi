import os
import requests
import json
from gtts import gTTS
import tempfile
from playsound import playsound

class VoiceflowAPI:
    def __init__(self):
        self.api_key = os.getenv('VOICEFLOW_API_KEY')
        if not self.api_key:
            raise ValueError("VOICEFLOW_API_KEY environment variable not set")
        
        self.base_url = 'https://general-runtime.voiceflow.com/state/user'
        self.user_id = 'budi-assistant'
        
    def send_transcription(self, transcription):
        """Send transcription to Voiceflow API and speak the response"""
        try:
            request = {
                'type': 'text',
                'payload': transcription
            }
            
            response = requests.post(
                f'{self.base_url}/{self.user_id}/interact',
                json={'request': request},
                headers={
                    'Authorization': self.api_key,
                    'versionID': 'production'
                }
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            # Extract and speak the response
            if response_data:
                for item in response_data:
                    if item.get('type') == 'text':
                        self.speak_text(item.get('payload'))
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error sending transcription to Voiceflow: {e}")
            return None

    def speak_text(self, text):
        """Convert text to speech and play it"""
        if not text:
            return
            
        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                # Generate speech
                tts = gTTS(text=text, lang='en')
                tts.save(fp.name)
                
                # Play the audio
                playsound(fp.name)
                
                # Clean up the temporary file
                os.unlink(fp.name)
        except Exception as e:
            print(f"Error in text-to-speech: {e}")