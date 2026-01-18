from time import sleep
from datetime import datetime
import os
import requests
import base64
import subprocess

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
        "-t", "1000"  # 2 seconds warm-up
    ]

    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print(f"Image saved as {filename}")
        return filepath
    except subprocess.CalledProcessError as e:
        print(f"Failed to capture image: {e}")
        return None

def upload_image_to_gemini(image_path, prompt, api_key):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()

    # Gemini expects base64-encoded image
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": encoded_image
                        }
                    }
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.ok:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Example usage after capturing image:
# api_key = "YOUR_GEMINI_API_KEY"
# prompt = "Describe the contents of this image."
# image_path = os.path.join(os.getcwd(), filename)
# result = upload_image_to_gemini(image_path, prompt, api_key)
# print(result)