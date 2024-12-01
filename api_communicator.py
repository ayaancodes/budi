import os
import requests
import json
from gtts import gTTS
import tempfile
from playsound import playsound
from dotenv import load_dotenv

load_dotenv()

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
                        message = item.get('payload', {}).get('message', '')
                        if message:
                            print(f"\nBudi: {message}")
                            self.speak_text(message)
            
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
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                # Generate speech with UK English accent (tends to be clearer and slightly faster)
                tts = gTTS(text=text, lang='en', tld='co.uk', slow=False)
                # Save to temporary file
                tts.save(temp_file.name)
                # Play the audio
                playsound(temp_file.name)
                # Clean up
                os.unlink(temp_file.name)
        except Exception as e:
            print(f"Error in text-to-speech: {e}")