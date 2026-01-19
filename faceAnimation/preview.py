import time
import threading
from unused.trigger import events, start_listener
import matplotlib.pyplot as plt
from animations import load_gif, Animation, Animator

idle = Animation(load_gif("assets/idle.gif"), loop=True)
no = Animation(load_gif("assets/no.gif"), loop=False)

animator = Animator({
    "idle": idle,
    "no": no
})

threading.Thread(
    target=start_listener,
    daemon=True
).start()

plt.ion()
fig, ax = plt.subplots()
ax.axis("off")

img_display = ax.imshow(idle.frames[0], cmap="gray")
fig.canvas.draw()
fig.canvas.flush_events()

FPS = 20
FRAME_DELAY = 0.0005

while True:
    while not events.empty():
        animator.switch(events.get_nowait())
    frame = animator.update()
    img_display.set_data(frame)

    fig.canvas.draw()
    fig.canvas.flush_events()
    time.sleep(FRAME_DELAY)