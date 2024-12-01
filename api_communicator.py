import requests

class APICommunicator:
    def __init__(self, cloudflare_url, voiceflow_url):
        self.cloudflare_url = cloudflare_url
        self.voiceflow_url = voiceflow_url

    def get_code_from_cloudflare(self):
        response = requests.get(self.cloudflare_url)
        if response.status_code == 200:
            return response.json()  # Adjust based on your API response
        else:
            return None

    def send_to_voiceflow(self, transcription, code):
        payload = {
            'transcription': transcription,
            'code': code
        }
        response = requests.post(self.voiceflow_url, json=payload)
        return response.status_code == 200