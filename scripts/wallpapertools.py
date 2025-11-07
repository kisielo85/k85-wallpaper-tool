import os
from PIL import Image
from screeninfo import get_monitors
import math
from dataclasses import dataclass
import pickle
import re
import subprocess
import time
import sys
from pathlib import Path

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
    center: Position
    primary: bool
    has_bind: bool
    bind_to: int = None
    bind_horizontal: bool = None
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

    data['min_pos'] = (min_x, min_y)
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

        if (
            (m2.pos.y < m.pos.y < m2.pos_end.y)
            or (m2.pos.y < m.pos_end.y < m2.pos_end.y)
            or (m.pos.y < m2.pos.y < m.pos_end.y)
            or (m.pos.y < m2.pos_end.y < m.pos_end.y)
        ):
            m.bind_horizontal = True
        else:
            m.bind_horizontal = False

        data['setup_order'].append([m.id, m2.id])


# process and save data from scale setup
def calculate_scale(s, lines):
    global data
    global temp_middle
    m1 = data['monitors'][s[0]]
    m2 = data['monitors'][s[1]]

    if (m1.bind_horizontal and m1.pos.x > m2.pos.x) or (not m1.bind_horizontal and m1.pos.y > m2.pos.y):
        lines[3], lines[1], lines[2], lines[0] = lines[2], lines[0], lines[3], lines[1]

    m1.scale = m2.scale * ((lines[3] - lines[1]) / (lines[2] - lines[0]))
    if m1.bind_horizontal:
        m1.relative_y = lines[1] - lines[0] * m1.scale
    else:
        m1.relative_x = lines[1] - lines[0] * m1.scale

    temp_middle[0] = (lines[0] + lines[2]) // 2
    temp_middle[1] = (lines[1] + lines[3]) // 2


# save data from gap setup
def save_gap(s, gap):
    global data
    m1 = data['monitors'][s[0]]
    m2 = data['monitors'][s[1]]

    m1.gap = gap

    if m1.bind_horizontal:
        if m1.pos.x < m2.pos.x:
            m1.relative_x = -gap * 2 - m1.width * m1.scale
        else:
            m1.relative_x = m2.width * m2.scale + gap * 2
    else:
        if m1.pos.y < m2.pos.y:
            m1.relative_y = -gap * 2 - m1.height * m1.scale
        else:
            m1.relative_y = m2.height * m2.scale + gap * 2


def verify_data(d):
    if (
        'canvas_size' not in d
        or 'setup_order' not in d
        or 'monitors' not in d
        or 'img_rectangles' not in d
        or 'img_size' not in d
        or 'min_pos' not in d
    ):
        return False

    for m in d['monitors']:
        if not m.has_bind:
            return False

    return True


def my_path():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    else:
        return Path(sys.argv[0]).resolve().parent

def load_data():
    global data
    try:
        with open(f"{my_path()}/k85WallpaperToolConfig.pkl", "rb") as f:
            d = pickle.load(f)
        if verify_data(d):
            data = d
            return True
    except:
        pass

    load_monitors()
    return False


def save_data():
    with open(f"{my_path()}/k85WallpaperToolConfig.pkl", "wb") as f:
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
def convert_wallpaper(src, info_txt=False, filename=False):
    out_path = os.path.dirname(src) + "/converted85_" + os.path.basename(src).split(".")[0]
    print(os.path.basename(src))
    video = "mp4" in src[src.rfind("."):].lower()

    calculate_img_conversion()
    global data
    rect = data['img_rectangles']
    save_data()

    if video:  # get source mp4 data: duration, fps, resolution
        out_path += ".mp4"
        try:
            src_x, src_y, fps, duration = (
                os.popen(
                    f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,duration -of csv=p=0 \"{src}\""
                )
                .read()
                .strip()
                .split(",")
            )
        except:
            return "no_ffmpeg", ""

        has_audio = (
            "audio"
            in os.popen(
                f'ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 \"{src}\"'
            ).read()
        )

        src_x = int(src_x)
        src_y = int(src_y)
    else:  # get source img resolution
        out_path += ".png"
        source_img = Image.open(src)
        src_x, src_y = source_img.size
        base_img = Image.new('RGB', data['canvas_size'])

    screen_x, screen_y = data['img_size'][0], data['img_size'][1]

    offset_x = 0
    offset_y = 0
    # check aspect ratio, crop so it's the same as in desired resolution
    if src_x / src_y < screen_x / screen_y:
        img_scale = src_x / screen_x
        offset_y = (src_y - screen_y * img_scale) // 2
    else:
        img_scale = src_y / screen_y
        offset_x = (src_x - screen_x * img_scale) // 2

    if video:  # preparing the ffmpeg command
        cmd = f"ffmpeg -f lavfi -i color=c=black:s={data['canvas_size'][0]}x{data['canvas_size'][1]}:r={fps}:d={duration}"
        cmd += f" -i \"{src}\" -filter_complex \""
        last = "0:v"

        for id, r in rect.items():
            from_x = int(r['from'][0] * img_scale + offset_x)
            from_y = int(r['from'][1] * img_scale + offset_y)
            to_x = int(r['to'][0] * img_scale + offset_x)
            to_y = int(r['to'][1] * img_scale + offset_y)
            m = data['monitors'][id]
            cmd += f"[1:v]crop={to_x-from_x}:{to_y-from_y}:{from_x}:{from_y},"
            cmd += (
                f"scale={m.width}:{m.height}[m{id}];[{last}][m{id}]overlay={m.pos.x}:{m.pos.y}[m{id}m];"
            )
            last = f"m{id}m"

        cmd += f"\" -map \"[{last}]:v\" {"-map 1:a " if has_audio else ""}-c:v libx264 -pix_fmt yuv420p -c:a copy \"{out_path}\" -y"

        fps, div = fps.split('/')
        fps = int(fps) / int(div)
        total_frames = int(fps * float(duration) + 0.99)
        fps_pattern = re.compile(r"frame=\s*([\d\.]+)")
        global eta
        eta = []

        # executing the command and checking progress
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)
        for line in process.stderr:
            fps_match = fps_pattern.search(line)
            if not fps_match:
                continue
            frame = int(fps_match.group(1))

            if info_txt:
                pr = frame * 100 / total_frames
                info_txt(f"processing {int(pr)}%\n{filename}\n{eeta(pr)}", False)

        process.wait()

    else:
        # creating new .png
        for id, r in rect.items():
            crop_area = (
                int(r['from'][0] * img_scale + offset_x),
                int(r['from'][1] * img_scale + offset_y),
                int(r['to'][0] * img_scale + offset_x),
                int(r['to'][1] * img_scale + offset_y),
            )
            m = data['monitors'][id]

            # copy area from source image and paste onto new wallpaper
            screen_img = source_img.crop(crop_area).resize((m.width, m.height), Image.LANCZOS)
            base_img.paste(screen_img, (m.pos.x, m.pos.y))

        base_img.save(out_path)

    return video, out_path


eta = []


def eeta(pr):
    nw = time.time()

    eta.append([nw, pr])
    if len(eta) > 20:
        eta.pop(0)

    progress = pr - eta[0][1]
    if progress != 0:
        elapsed = nw - eta[0][0]
        t_left = int(elapsed * (100 - pr) / progress)
        minute = int(t_left / 60)
        return f"{f"{minute}min " if minute !=0 else ""}{t_left-minute*60}s"
    return f"..."
