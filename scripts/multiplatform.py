import platform, os, ctypes
from tkinter import filedialog

system = desktop_env = platform.system()
if system == "Linux":
    desktop_env = os.getenv("XDG_CURRENT_DESKTOP", "").lower()
# fmt: off

def set_wallpaper_span():
    if desktop_env == "Windows":
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "22")
            winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
    
    elif "gnome" in desktop_env:
        os.system("gsettings set org.gnome.desktop.background picture-options spanned")
    
    elif "cinnamon" in desktop_env:
        os.system("gsettings set org.cinnamon.desktop.background picture-options spanned")
    
    elif "mate" in desktop_env:
        os.system(f"gsettings set org.mate.background picture-options spanned")
        
    else:
        print("not supported:", system, desktop_env)
        return False
    return True


def set_wallpaper(image_path = "wallpaper.png"):
    image_path = os.path.abspath(image_path)

    if desktop_env == "Windows":
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0x01)
    
    elif "gnome" in desktop_env:
        os.system(f'gsettings set org.gnome.desktop.background picture-uri "file://{image_path}"')

    elif "cinnamon" in desktop_env:
        os.system(f'gsettings set org.cinnamon.desktop.background picture-uri "file://{image_path}"')

    elif "mate" in desktop_env:
        os.system(f'gsettings set org.mate.background picture-filename "{image_path}"')

    else:
        print("not supported:", system, desktop_env)
        return False
    return True


def get_file():
    match system:
        case "Windows":
            return filedialog.askopenfilename(filetypes=[('', '*.jpg;*.jpeg;*.png'), ('All Files', '*')])
        
        case "Linux":
            return (os.popen("zenity --file-selection --file-filter='Image files (png, jpg, jpeg) | *.png *.jpg *.jpeg' --file-filter='All files | *'").read().strip())
        
        case _:
            print("not supported:", system)
            return False
