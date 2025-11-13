#!/bin/bash
read -p "version: v" v
pyinstaller --onefile --name="k85.wallpaper.tool.linux.v${v}" --add-data "assets/*_img.png:assets" --add-data "assets/icon.png:assets" --hidden-import PIL._tkinter_finder --collect-all tkinterdnd2 --noconfirm --noconsole main.py