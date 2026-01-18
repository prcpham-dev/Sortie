from datetime import datetime
import os
import subprocess
from google import genai
from google.genai import types
from camera.config import *

client = genai.Client(api_key=GOOGLE_API_KEY)

def capture(filename, filepath, width=800, height=600) -> str:
    # Generate a filename based on the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"image_{timestamp}.jpg" if filename != "" else filename
    filepath = os.path.join(os.getcwd(), filename) if filepath != "" else filepath

    # Build the rpicam command
    cmd = [
        "rpicam-jpeg",
        "-o", filepath,
        "--width", str(width),
        "--height", str(height),
        "--quality", "75",
        "-t", "150"  # 2 seconds warm-up
    ]

    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print(f"Image saved as {filename}")
        return filepath
    except subprocess.CalledProcessError as e:
        print(f"Failed to capture image: {e}")
        return None

def upload_image_to_gemini(image_path, prompt):
    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    response = client.models.generate_content(
        model='gemini-3-flash-preview',
        contents=[
            types.Part.from_bytes(
            data=image_bytes,
            mime_type='image/jpeg',
            ),
            prompt
        ]
    )

    print(response.text)