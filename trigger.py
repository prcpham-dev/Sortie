import queue, threading
from gpiozero import Button
from signal import pause
from camera.camera import *
from config import *

events = queue.Queue()
busy = threading.Lock()
responses = queue.Queue()

def run_process():
    print("Run capture")
    result = capture("test1.jpg", "./")
    print(result)
    PROMPT="Describe this image in less than 10 words."
    response = upload_image_to_gemini(result, PROMPT, GOOGLE_API_KEY)
    
    responses.put(response)
    events.put("idle")
    busy.release()
        
def on_button_press():
    print("Button pressed")
    if busy.locked():
        return
    
    busy.acquire()
    events.put("no")
    threading.Thread(target=run_process, daemon=True).start()

def start_listener():
    btn = Button(17, pull_up=True)
    btn.when_pressed = on_button_press