from picamera import PiCamera
from time import sleep
from datetime import datetime
import os

def capture(width=800, height=600):
    # Initialize the camera
    camera = PiCamera()

    # Optional: set resolution 1024 x 768
    camera.resolution = (width, height)

    # Let the camera warm up for 2 seconds
    sleep(2)

    # Generate a filename based on the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"image_{timestamp}.jpg"

    # Capture the image and save it in the same directory
    camera.capture(os.path.join(os.getcwd(), filename))

    print(f"Image saved as {filename}")

