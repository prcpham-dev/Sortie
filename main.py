import time
import threading
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1309
from gpiozero import Button
from camera.camera import capture, upload_image_to_gemini
from config import GOOGLE_API_KEY
from faceAnimation.animations import load_gif, Animation, Animator

# OLED setup
serial = i2c(port=1, address=0x3C)
device = ssd1309(serial, width=128, height=64)

# Animations
idle = Animation(load_gif("faceAnimation/assets/idle.gif"), loop=True)
no = Animation(load_gif("faceAnimation/assets/no.gif"), loop=True)

animator = Animator(
    {
        "idle": idle,
        "no": no
    },
    default="idle"
)

# Button setup
btn = Button(17, pull_up=True)

def run_process_and_animate():
    print("Button pressed")
    animator.switch("no")
    # Switch back to idle after a short delay, regardless of process completion
    def reset_animation():
        time.sleep(1)  # Show "no" animation for 1 second
        animator.switch("idle")
    threading.Thread(target=reset_animation, daemon=True).start()

    # Run capture and upload in a separate thread
    def process():
        print("Run capture")
        result = capture("test1.jpg", "./")
        print(result)
        PROMPT = "Describe this image in less than 10 words."
        if result:
            upload_image_to_gemini(result, PROMPT, GOOGLE_API_KEY)
    threading.Thread(target=process, daemon=True).start()

btn.when_pressed = run_process_and_animate

FPS = 25
FRAME_DELAY = 1 / FPS

print("Ready to press button for animation and capture.")

while True:
    frame = animator.update()
    device.display(frame)
    time.sleep(FRAME_DELAY)
