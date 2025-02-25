from PIL import Image, ImageTk
from pynput import keyboard
import tkinter as tk
import sys, os

temp_middle = [0, 0]


# proper file path for .exe version
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# prepare canvas
def get_canvas_base(data, master, mode="scale"):
    canvas_x, canvas_y = data['canvas_size']
    min_x, min_y = data['min_pos']

    window = tk.Toplevel(master)
    window.geometry(f"{canvas_x}x{canvas_y}+{min_x}+{min_y}")
    window.overrideredirect(True)
    if sys.platform == "win32":
        window.attributes("-transparentcolor", "gray")

    canvas = tk.Canvas(
        window, width=canvas_x, height=canvas_y, bg="black", highlightthickness=0
    )

    # draw instructions on every screen
    img_path = "assets/scale_img.png" if mode == "scale" else "assets/gap_img.png"

    canvas.images = []
    for m in data['monitors']:
        # resize and center img
        img = Image.open(resource_path(img_path))
        x, y = img.size
        new_x = int(m.width * 0.3)
        img = img.resize((new_x, int(new_x / x * y)))
        x, y = img.size
        img = ImageTk.PhotoImage(img)
        canvas.create_image(
            m.center.x - x // 2, m.center.y - y // 2, anchor=tk.NW, image=img
        )
        canvas.images.append(img)

    canvas.pack()
    window.lift()
    window.focus_force()
    return window, canvas


# UI for getting display scale
def get_scale(data, screens, master):
    out = False
    dragging_line = False
    window, canvas = get_canvas_base(data, master, "scale")

    # draw horizontal lines
    lines = []
    offset = []
    for i in range(2):
        for s in screens:
            m = data['monitors'][s]

            y = m.pos_end.y - 20 if i else m.pos.y + 20
            fill = "red" if i else "blue"

            offset.append(m.pos.y)
            lines.append(
                canvas.create_line(m.pos.x, y, m.pos_end.x, y, fill=fill, width=6)
            )
    previous_line = lines[0]

    def on_mouse_press(event):
        nonlocal dragging_line, previous_line
        # check if there is a line nearby to grab
        for line in lines:
            x1, y, x2, _ = canvas.coords(line)
            if abs(event.y - y) < 20 and x1 < event.x < x2:
                dragging_line = line
                previous_line = line
                set_cursor("fleur")
                break

    def on_mouse_drag(event):
        nonlocal dragging_line
        if dragging_line:
            y = event.y
            x1, _, x2, _ = canvas.coords(dragging_line)
            canvas.coords(dragging_line, x1, y, x2, y)

    def on_mouse_release(event):
        nonlocal dragging_line
        dragging_line = None
        set_cursor("arrow")

    def move_line(val):
        nonlocal previous_line
        if previous_line:
            x1, y, x2, _ = canvas.coords(previous_line)
            y += val
            canvas.coords(previous_line, x1, y, x2, y)

    def close(canceled=False):
        nonlocal out
        listener.stop()
        if canceled:
            out = False
            window.destroy()
            return

        out = []
        for i, line in enumerate(lines):
            _, y, _, _ = canvas.coords(line)
            out.append(int(y))

        # save middle coordinates for gap configuration
        global temp_middle
        temp_middle[0] = (out[0] + out[2]) // 2
        temp_middle[1] = (out[1] + out[3]) // 2

        for i in range(4):
            out[i] -= offset[i]

        window.destroy()
        return

    def set_cursor(cursor):
        canvas.config(cursor=cursor)

    for line in lines:
        canvas.tag_bind(line, "<Enter>", lambda event: set_cursor("fleur"))
        canvas.tag_bind(line, "<Leave>", lambda event: set_cursor("arrow"))

    def on_press(key):
        match key:
            case keyboard.Key.left | keyboard.Key.down:
                move_line(1)
            case keyboard.Key.right | keyboard.Key.up:
                move_line(-1)
            case keyboard.Key.esc:
                close(canceled=True)
            case keyboard.Key.enter:
                close()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    window.bind("<ButtonPress-1>", on_mouse_press)
    window.bind("<B1-Motion>", on_mouse_drag)
    window.bind("<ButtonRelease-1>", on_mouse_release)
    master.wait_window(window)

    return out


# UI for getting space between monitors
def get_gap(data, s, master):
    drag_from = -1
    multiplier = 0
    middle = data['monitors'][s[0]].pos_end.x
    window, canvas = get_canvas_base(data, master, "gap")

    # draw diagonal lines
    gap = 20
    lines = []
    for i in range(4):
        s_id = i % 2
        m = data['monitors'][s[s_id]]
        len = m.width * 2

        x2 = m.pos.x + 2 if i % 2 else m.pos_end.x - 2
        y2 = temp_middle[s_id]
        x1 = x2 + (len if i % 2 else -len)
        y1 = y2 + (-len if i < 2 else len)

        fill = 'blue' if 0 < i < 3 else 'red'
        lines.append(canvas.create_line(x1, y1, x2, y2, fill=fill, width=6))

    def on_mouse_press(event):
        nonlocal drag_from, multiplier
        multiplier = 1 if event.x > middle else -1
        drag_from = event.x

    def on_mouse_drag(event):
        nonlocal drag_from, gap
        if drag_from != -1:
            move = (drag_from - event.x) * multiplier
            gap += move
            drag_from = event.x
            update_lines()

    # used by arrows
    def move_gap(val):
        nonlocal gap
        gap += val
        update_lines()

    # draw lines according to the gap variable
    def update_lines():
        for i, line in enumerate(lines):
            x1, y1, x2, y2 = canvas.coords(line)

            y2 = temp_middle[i % 2] + (-gap if i < 2 else +gap)
            y1 = y2 + (x1 - x2) * (-1 if 0 < i < 3 else 1)

            canvas.coords(line, x1, y1, x2, y2)

    def close(canceled=False):
        nonlocal gap
        listener.stop()
        if canceled:
            gap = False
        window.destroy()

    def on_press(key):
        match key:
            case keyboard.Key.left | keyboard.Key.down:
                move_gap(-1)
            case keyboard.Key.right | keyboard.Key.up:
                move_gap(1)
            case keyboard.Key.esc:
                close(canceled=True)
            case keyboard.Key.enter:
                close()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    window.bind("<ButtonPress-1>", on_mouse_press)
    window.bind("<B1-Motion>", on_mouse_drag)
    window.bind("<ButtonRelease-1>", lambda e: update_lines())
    canvas.config(cursor="fleur")
    update_lines()
    master.wait_window(window)

    if gap != False:
        return gap + 2
    else:
        return False
