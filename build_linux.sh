#!/bin/bash
read -p "version: v" v
pyinstaller --onefile --name="k85.wallpaper.tool.linux.v${v}" --add-data "assets/*_img.png:assets" --add-data "assets/icon.png:assets" --noconfirm --noconsole main.py