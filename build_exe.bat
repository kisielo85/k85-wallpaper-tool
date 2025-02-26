set /p v=version: v
pyinstaller --onefile --icon=assets/icon.png --name="k85.wallpaper.tool.%v%" --add-data "assets/*_img.png:assets" --noconfirm --noconsole main.py