import time
import threading
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1309

from animations import load_gif, Animation, Animator
from unused.trigger import events, start_listener

serial = i2c(port=1, address=0x3C)
device = ssd1309(serial, width=128, height=64)

idle = Animation(load_gif("faceAnimation/assets/idle.gif"), loop=True)
thinking = Animation(load_gif("faceAnimation/assets/thinking.gif"), loop=True)
grabage = Animation(load_gif("faceAnimation/assets/grabage.gif"), loop=False)
recycle = Animation(load_gif("faceAnimation/assets/recycle.gif"), loop=False)

animator = Animator(
    {
        "idle": idle,
        "thinking": thinking,
        "grabage": grabage,
        "recycle": recycle
    },
    default="idle"
)

threading.Thread(
    target=start_listener,
    daemon=True
).start()


FPS = 25
FRAME_DELAY = 1 / FPS

while True:
    while not events.empty():
        animator.switch(events.get_nowait())

    frame = animator.update()
    device.display(frame)
    time.sleep(FRAME_DELAY)
