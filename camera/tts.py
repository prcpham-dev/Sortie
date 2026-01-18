from elevenlabs.client import ElevenLabs
from config import *

client = ElevenLabs(api_key=ELEVENLABS)

def convert_to_speech():
    # Get raw response with headers
    response = client.text_to_speech.with_raw_response.convert(
        text="Hello, world!",
        voice_id="voice_id"
    )

    # Access character cost from headers
    char_cost = response.headers.get("x-character-count")
    request_id = response.headers.get("request-id")
    audio_data = response.data
