import ctypes
import os
from PIL import Image, ImageDraw, ImageFont
from screeninfo import get_monitors
import math
from dataclasses import dataclass
import pickle
from sys import platform


base_img = False
temp_middle = [0, 0]
data = False


@dataclass
class Position:
    x: int
    y: int

    def arr(self):
        return (self.x, self.y)


@dataclass
class Monitor:
    id: int
    pos: Position
    pos_end: Position
    height: int
    width: int
    primary: bool
    has_bind: bool
    center: Position
    bind_to: int = None
    gap: int = 0
    scale: float = 1.0
    relative_y: int = 0
    relative_x: int = 0


# returns id of the closest display with/without a bind
def get_closest(id, bind=True):
    center = data['monitors'][id].center.arr()

    closest = False
    closest_id = -1
    for m in data['monitors']:
        if m.has_bind != bind or m.id == id:
            continue
        dist = math.dist(center, m.center.arr())

        if not closest or dist < closest:
            closest_id = m.id
            closest = dist

    return closest_id


# saves all important stuff to data variable
def load_monitors():
    global data
    data = {'monitors': []}

    monitors = get_monitors()
    min_x = max_x = min_y = max_y = 0
    primary_id = 0

    # getting display data
    for i, m in enumerate(monitors):
        # smallest and largest cords - used to calculate canvas size
        min_x = min(min_x, m.x)
        min_y = min(min_y, m.y)
        max_x = max(max_x, m.x + m.width)
        max_y = max(max_y, m.y + m.height)

        if m.is_primary:
            primary_id = i

        data['monitors'].append(
            Monitor(
                id=i,
                pos=Position(m.x, m.y),
                pos_end=Position(0, 0),
                height=m.height,
                width=m.width,
                primary=m.is_primary,
                has_bind=m.is_primary,
                center=Position(0, 0),
            )
        )

    # modify coordinates for easier canvas usage
    for i, m in enumerate(data['monitors']):
        m.pos.x -= min_x
        m.pos.y -= min_y
        m.pos_end = Position(m.pos.x + m.width - 1, m.pos.y + m.height - 1)
        m.center.x = m.pos.x + m.width // 2
        m.center.y = m.pos.y + m.height // 2

    data['canvas_size'] = (max_x - min_x, max_y - min_y)
    data['setup_order'] = []

    # order in which monitors will be configured
    while True:
        m_id = get_closest(primary_id, False)
        if m_id == -1:
            break

        m = data['monitors'][m_id]
        m2 = data['monitors'][get_closest(m_id, True)]
        m.bind_to = m2.id
        m.has_bind = True

        data['setup_order'].append(
            [m.id, m2.id] if m.pos.x < m2.pos.x else [m2.id, m.id]
        )


# creates a blank cavas with green monitor outlines
def get_base_image():
    global data

    if not data:
        load_monitors()

    template = Image.new('RGB', data['canvas_size'])
    draw = ImageDraw.Draw(template)

    # outlines
    for m in data['monitors']:
        rect_from = m.pos.arr()
        rect_to = m.pos_end.arr()
        draw.rectangle([rect_from, rect_to], outline='green')

    base_img = template
    return base_img.copy()


def set_wallpaper(image_path):
    image_path = os.path.abspath(image_path)
    print(image_path,platform)
    if platform == "linux" or platform == "linux2":
        os.system(f"gsettings set org.gnome.desktop.background picture-uri file://{image_path}")
        print(f"gsettings set org.gnome.desktop.background picture-uri file://{image_path}")
    elif platform == "win32":
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0x01)


# draws red and blue lines, used for getting a scale
def draw_scale_setting(s, lines=False):
    global data
    img = get_base_image()
    draw = ImageDraw.Draw(img)

    # default line positions
    if not lines:
        lines = [
            20,
            20,
            data['monitors'][s[0]].height - 60,
            data['monitors'][s[1]].height - 60,
        ]

    # drawing
    for i, line_y in enumerate(lines):
        m = data['monitors'][s[i % 2]]
        fill = 'blue' if i < 2 else 'red'

        line_from = (m.pos.x, m.pos.y + line_y)
        line_to = (m.pos_end.x, m.pos.y + line_y)

        draw.line([line_from, line_to], width=3, fill=fill)
        font = ImageFont.truetype('arial_bold.ttf', 50)

        txt_x = line_from[0] + 15 if i % 2 else line_to[0] - 45
        txt_y = line_from[1] if i < 2 else line_from[1] - 70
        draw.text((txt_x, txt_y), str(i % 2 + 1), font=font, fill=fill)

    # set new image
    try:
        img.save('temp.png')
        set_wallpaper('temp.png')
        print('wallpaper set')
    except:
        print('error while setting wallpaper')

    return lines


# process and save data from ScaleUI
def calculate_scale(s, lines):
    global data
    global temp_middle
    m1 = data['monitors'][s[0]]
    m2 = data['monitors'][s[1]]

    # make sure m1 is the one being set
    if m2.bind_to == m1.id:
        m1, m2 = m2, m1
        lines[0], lines[1] = lines[1], lines[0]
        lines[2], lines[3] = lines[3], lines[2]

    m1.scale = m2.scale * (lines[3] - lines[1]) / (lines[2] - lines[0])
    m1.relative_y = lines[1] - lines[0] * m1.scale

    temp_middle[0] = (lines[0] + lines[2]) // 2
    temp_middle[1] = (lines[1] + lines[3]) // 2


# draws diagonal lines, used for meassuring gaps between screens
def draw_gap_setting(s, gap=0):
    global data
    img = get_base_image()
    draw = ImageDraw.Draw(img)

    # some funky math for drawing diagonal lines
    for i in range(4):
        s_id = i % 2
        m = data['monitors'][s[s_id]]
        x1 = x2 = m.pos.x
        y1 = m.pos.y
        y2 = m.pos.y + temp_middle[s_id]

        if i < 2:
            x1 += (-temp_middle[s_id] + gap) * (1 if i == 0 else -1)
            y2 += -gap - 2
        else:
            x1 += (-m.height + temp_middle[s_id] + gap) * (1 if i == 2 else -1)
            y1 += m.height
            y2 += gap + 2
        if s_id == 0:
            x1 += m.width
            x2 += m.width - 2
        else:
            x2 += 2

        draw.line([(x1, y1), (x2, y2)], width=3, fill='blue' if 0 < i < 3 else 'red')

    try:
        img.save('temp.png')
        set_wallpaper('temp.png')
        print('wallpaper set')
    except:
        print('error while setting wallpaper')

    return gap


# save data from GapUI
def save_gap(s, gap):
    global data
    m1 = data['monitors'][s[0]]
    m2 = data['monitors'][s[1]]

    # make sure m1 is the one being set
    if m2.bind_to == m1.id:
        m1, m2 = m2, m1

    m1.gap = gap

    if m1.pos.x < m2.pos.x:
        m1.relative_x = -gap * 2 - m1.width * m1.scale
    else:
        m1.relative_x = m2.width * m2.scale + gap * 2


def verify_data(d):
    if (
        'canvas_size' not in d
        or 'setup_order' not in d
        or 'monitors' not in d
        or 'img_rectangles' not in d
        or 'img_size' not in d
    ):
        return False

    for m in d['monitors']:
        if not m.has_bind:
            return False

    return True


def load_data():
    global data
    try:
        with open("data.pkl", "rb") as f:
            d = pickle.load(f)
        if verify_data(d):
            data = d
            return True
    except:
        pass

    load_monitors()
    return False


def save_data():
    with open("data.pkl", "wb") as f:
        pickle.dump(data, f)


# calculates what areas of the original image
# should be copied and pasted onto the wallpaper
def calculate_img_conversion():
    global data
    rect = {}
    min_x = min_y = 0

    # get primary monitor first, at cords 0, 0
    for m in data['monitors']:
        if m.primary:
            rect[m.id] = {
                'from': [0, 0],
                'to': [m.width, m.height],
            }
            break

    # calculate screen positions and sizes
    for o in data['setup_order']:
        m1 = data['monitors'][o[0]]
        m2 = data['monitors'][o[1]]
        if m2.bind_to == m1.id:
            m1, m2 = m2, m1

        pos = rect[m2.id]['from'].copy()
        pos[0] += m1.relative_x
        pos[1] += m1.relative_y
        min_x = min(min_x, pos[0])
        min_y = min(min_y, pos[1])

        rect[m1.id] = {
            'from': [pos[0], pos[1]],
            'to': [
                pos[0] + m1.width * m1.scale,
                pos[1] + m1.height * m1.scale,
            ],
        }

    # convert cords and get desired image size
    max_x = max_y = 0
    for r in rect:
        for point in rect[r]:
            rect[r][point][0] -= min_x
            rect[r][point][1] -= min_y
            max_x = max(max_x, rect[r][point][0])
            max_y = max(max_y, rect[r][point][1])

    data['img_rectangles'] = rect
    data['img_size'] = [max_x, max_y]


# converts image to wallpaper
def convert_wallpaper(img):
    calculate_img_conversion()
    global data
    rect = data['img_rectangles']
    save_data()
    source_img = Image.open(img)

    img_x, img_y = source_img.size
    screen_x, screen_y = data['img_size'][0], data['img_size'][1]

    # check aspect ratio, crop so it's the same as in desired resolution
    if img_x / img_y < screen_x / screen_y:
        img_scale = img_x / screen_x
        crop_px = (img_y - screen_y * img_scale) // 2
        source_img = source_img.crop((0, crop_px, img_x, img_y - crop_px))
    else:
        img_scale = img_y / screen_y
        crop_px = (img_x - screen_x * img_scale) // 2
        source_img = source_img.crop((crop_px, 0, img_x - crop_px, img_y))
    
    # creating new .png
    base_img = get_base_image()
    for id, r in rect.items():
        crop_area = (
            r['from'][0] * img_scale,
            r['from'][1] * img_scale,
            r['to'][0] * img_scale,
            r['to'][1] * img_scale,
        )
        m = data['monitors'][id]

        # copy area from source image and paste onto new wallpaper
        screen_img = source_img.crop(crop_area).resize(
            (m.width, m.height), Image.LANCZOS
        )
        base_img.paste(screen_img, (m.pos.x, m.pos.y))

    base_img.save("wallpaper.png")
    return "wallpaper.png"
