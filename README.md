# k85 wallpaper tool

a simple wallpaper tool for multiple monitors that takes into account different screen sizes and spaces between them
<br><br>
Compatible with:

* Windows 10 / 11
* Linux Gnome / Cinnamon / Mate

on other enviroments you're gonna have to manually set wallpaper mode to "spanned" and use the created .png file

## Installation

### Windows

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

### Linux

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
