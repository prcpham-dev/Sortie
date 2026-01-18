import time, re
import threading
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1309
from gpiozero import Button
from camera.camera import capture, upload_image_to_gemini
from config import GOOGLE_API_KEY
from faceAnimation.animations import load_gif, Animation, Animator

# Gemini prompt
PROMPT="""
You are a waste-sorting assistant.

Analyze the image and identify which bin the item should go to.

Assign exactly ONE bin from the following list:
  - recycle
  - garbage
  - paper
  - compost
In case of multiple items (a paper box with plastic lids), just assign "garbage"

Rules:
- Do NOT explain your reasoning.
- Do NOT include items you are unsure about.
- Do NOT invent new bin types.
- If an item has multiple parts, list each part separately.

Language requirement:
- Answer in English, using 1 word only (the name of the bin)
- Answer in all caps
- Do NOT include emojis
"""

# OLED setup
serial = i2c(port=1, address=0x3C)
device = ssd1309(serial, width=128, height=64)

# Animations
idle = Animation(load_gif("faceAnimation/assets/idle.gif"), loop=True)
thinking = Animation(load_gif("faceAnimation/assets/thinking.gif"), loop=True)
transition = Animation(load_gif("faceAnimation/assets/transition.gif"), loop=False)
transition_recycle = Animation(load_gif("faceAnimation/assets/transition_recycle.gif"), loop=False)

trash = Animation(load_gif("faceAnimation/assets/trash.gif"), loop=True)
recycle = Animation(load_gif("faceAnimation/assets/recycle.gif"), loop=True)
paper = Animation(load_gif("faceAnimation/assets/paper.gif"), loop=True)
compost = Animation(load_gif("faceAnimation/assets/food.gif"), loop=True)
overwhelmed = Animation(load_gif("faceAnimation/assets/overwhelmed.gif"), loop=True)


animator = Animator(
    {
        "idle": idle,
        "thinking": thinking,
        "transition": transition,
        "transition_recycle": transition_recycle,
        "paper": paper,
        "trash": trash,
        "recycle": recycle,
        "compost": compost,
        "overwhelmed": overwhelmed
    },
    default="idle"
)

def apply_response(resp):
    text = resp.lower()
    if re.search(r"\brecycle\b", text, re.I):
        animator.switch("transition_recycle", force=True)
        animator.switch("recycle")
        time.sleep(4)
    elif re.search(r"\btrash\b", text, re.I):
        animator.switch("transition", force=True)
        animator.switch("trash")
        time.sleep(4)
    elif re.search(r"\bpaper\b", text, re.I):
        animator.switch("transition", force=True)
        animator.switch("paper")
        time.sleep(4)
    elif re.search(r"\bcompost\b", text, re.I):
        animator.switch("transition", force=True)
        animator.switch("compost")
        time.sleep(4)
    else:
        animator.switch("overwhelmed", force=True)
        time.sleep(5)

# Button setup
btn = Button(17, pull_up=True)

def run_process_and_animate():
    print("Button pressed")
    animator.switch("thinking")
    resp = "EROOR"
    def process():
        print("Run capture")
        result = capture("./data")
        print(result)
        if result:
            resp = upload_image_to_gemini(result, PROMPT, GOOGLE_API_KEY)
        apply_response(resp)
        animator.switch("idle")

    threading.Thread(target=process, daemon=True).start()



btn.when_pressed = run_process_and_animate

FPS = 25
FRAME_DELAY = 1 / FPS

print("Ready to press button for animation and capture.")

while True:
    frame = animator.update()
    device.display(frame)
    time.sleep(FRAME_DELAY)
