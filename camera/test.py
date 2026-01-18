import os
import requests
import subprocess
from google import genai
from google.genai import types
from elevenlabs.client import ElevenLabs
from config import *

# ---------------- CONFIG ----------------
GEMINI_API_KEY = GOOGLE_API_KEY
ELEVEN_API_KEY = ELEVENLABS

VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Rachel
MODEL = "gemini-3-flash-preview"

# ---------------------------------------

gemini = genai.Client(api_key=GEMINI_API_KEY)
elevenlabs = ElevenLabs(api_key=ELEVEN_API_KEY)
session = requests.Session()


def elevenlabs_stream_tts(text: str):
    """
    Stream audio from ElevenLabs and play immediately.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.7,
        },
    }

    # mpg123 reads MP3 frames from stdin
    player = subprocess.Popen(
        ["mpg123", "-q", "-"],
        stdin=subprocess.PIPE
    )

    with session.post(
        url,
        json=payload,
        headers=headers,
        stream=True,
        timeout=(2, 8)
    ) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                player.stdin.write(chunk)

    player.stdin.close()
    player.wait()


def stream_gemini_and_speak(image_bytes: bytes, prompt: str):
    """
    Stream Gemini output, send partial sentences to ElevenLabs.
    """
    stream = gemini.models.generate_content_stream(
        model=MODEL,
        contents=[
            prompt,
            types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg",
            ),
        ],
    )

    buffer = ""

    for event in stream:
        if not event.text:
            continue

        buffer += event.text

        # Speak as soon as we hit a sentence boundary
        if any(p in buffer for p in [".", "!", "?"]):
            sentence = buffer.strip()
            buffer = ""

            print("🗣 Speaking:", sentence)
            elevenlabs_stream_tts(sentence)

    # Speak any remainder
    if buffer.strip():
        elevenlabs_stream_tts(buffer.strip())


# ----------------- USAGE -----------------

PROMPT = """
Describe this image in 20 words.
"""

with open("test.jpg", "rb") as f:
    image = f.read()

stream_gemini_and_speak(image, PROMPT)
