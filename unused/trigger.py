import queue, sys
from gpiozero import Button
from signal import pause
from camera.camera import *
from config import *

def trigger(name):
    """
    Public API to trigger an animation.
    Can be called from anywhere.
    """
    events.put(name)

def start_listener():
    """
    Temporary ENTER listener.
    Replace later with GPIO / audio / AI.
    """
    print("Press ENTER to say NO")
    while True:
        sys.stdin.readline()
        events.put("no")

events = queue.Queue()
responses = queue.Queue()

def run_process():
    print("Run capture")
    result = capture("test1.jpg", "./")
    print(result)
    PROMPT="Describe this image in less than 10 words."
    response = upload_image_to_gemini(result, PROMPT, GOOGLE_API_KEY)
    responses.put(response)
    print(responses.get_nowait())

        
def on_button_press():
    print("Button pressed")
    run_process()

btn = Button(17, pull_up=True)
print("Ready to press")
btn.when_pressed = on_button_press
pause()