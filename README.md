# k85 wallpaper tool

If you ever wanted to set a wallpaper that would span across multiple monitors, you probably know how hard it is to make it look seamless. That's where this tool comes in handy. After a quick and easy setup, it calculates the differences in display sizes and the gaps between them, allowing you to set a perfectly aligned wallpaper.


| Before                                              | After                                             |
| ----------------------------------------------------- | --------------------------------------------------- |
| ![wallpaper before](assets/github_img/1_before.jpg) | ![wallpaper after](assets/github_img/1_after.jpg) |

The setup works by displaying lines that the user manually aligns. This only needs to be done once, as the configuration is saved for future use.

![configuration gif](assets/github_img/setup.gif)
<br>


| Before                                              | After                                             |
| ----------------------------------------------------- | --------------------------------------------------- |
| ![wallpaper before](assets/github_img/2_before.jpg) | ![wallpaper after](assets/github_img/2_after.jpg) |
| ![wallpaper before](assets/github_img/3_before.jpg) | ![wallpaper after](assets/github_img/3_after.jpg) |
| ![wallpaper before](assets/github_img/4_before.jpg) | ![wallpaper after](assets/github_img/4_after.jpg) |


| wallpaper                                                                                              | artist                                                           |
| -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| [image1](https://www.reddit.com/media?url=https%3A%2F%2Fi.redd.it%2Fg9mkm42rvu0b1.jpg)                 | [kvacm](https://www.instagram.com/kvacm)                         |
| [image2](https://www.freepik.com/free-vector/night-ocean-landscape-full-moon-stars-shine_17740155.htm) | [BGMotion_Utube](https://www.youtube.com/@BGMotion_Utube/videos) |
| [image3](https://www.behance.net/gallery/48555649/80s-Pantera)                                         | [DTM_Illustration](https://www.behance.net/deto)                 |
| [image4](https://www.pixiv.net/en/artworks/84466005)                                                   | [KRYP_132](https://www.pixiv.net/en/users/16096005)           |

Compatible with:

* Windows 10 / 11
* Linux Gnome / Cinnamon / Mate

on other enviroments you're gonna have to manually set wallpaper mode to "spanned" and use the created .png file

## Installation

<details open>
<summary>Windows</summary>

#### Option 1: .exe file

1. go to the [Releases](https://github.com/kisielo85/k85-wallpaper-tool/releases) page
2. download and run the latest .exe file

#### Option 2: running with python

1. Install [Python](https://www.python.org/downloads/)
2. Download and unpack [.zip repository](https://github.com/kisielo85/k85-wallpaper-tool/archive/refs/heads/main.zip) or use `git clone`
   ```cmd
   git clone https://github.com/kisielo85/k85-wallpaper-tool
   cd k85-wallpaper-tool
   ```
3. Create virtual enviroment (optional)
   ```cmd
   py -m venv venv
   venv\Scripts\activate
   ```
4. Install requirements
   ```cmd
   pip install -r requirements.txt
   ```
5. Run script
   ```bash
   py main.py
   ```
</details>

<details>
<summary>Linux</summary>

1. Install dependencies
   ```bash
   sudo apt update
   apt install zenity python3 python3-pip python3-venv python3-tk
   ```
2. Download and unpack [.zip repository](https://github.com/kisielo85/k85-wallpaper-tool/archive/refs/heads/main.zip) or use `git clone`
   ```bash
   git clone https://github.com/kisielo85/k85-wallpaper-tool
   cd k85-wallpaper-tool
   ```
3. Create virtual enviroment
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install requirements
   ```bash
   pip install -r requirements.txt
   ```
5. Run script
   ```bash
   python3 main.py
   ```
</details>
