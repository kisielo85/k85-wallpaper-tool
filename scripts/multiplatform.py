import platform, os, ctypes
from tkinter import filedialog

system = platform.system()


def set_wallpaper_span():
    print(system)

    match system:
        case "Windows":
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Control Panel\Desktop",
                0,
                winreg.KEY_SET_VALUE,
            ) as key:
                winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "22")
                winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")

        case "Linux":
            desktop_env = os.getenv("XDG_CURRENT_DESKTOP", "").lower()
            print("env:", desktop_env)

            match desktop_env:
                case "cinnamon" | "x-cinnamon" | "cinnamon-session" | "cinnamon2d":
                    os.system(
                        "gsettings set org.cinnamon.desktop.background picture-options spanned"
                    )

                case "gnome" | "ubuntu" | "gnome-session":
                    os.system(
                        "gsettings set org.gnome.desktop.background picture-options spanned"
                    )

                case "kde":
                    os.system(
                        'qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "var Desktops = desktops(); for (i=0; i<Desktops.length; i++) { Desktops[i].wallpaperPlugin = \'org.kde.image\'; Desktops[i].currentConfigGroup = Array(\'Wallpaper\', \'org.kde.image\', \'General\'); Desktops[i].writeConfig(\'FillMode\', 6); }"'
                    )

                case "xfce":
                    os.system(
                        'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-style -s 5'
                    )

                case _:
                    print("enviroment not supported:", desktop_env)
                    return False
        case _:
            print("OS not supported:", system)
            return False

    return True


def set_wallpaper(image_path):
    image_path = os.path.abspath(image_path)
    match system:
        case "Windows":
            ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0x01)
        case "Linux":
            desktop_env = os.getenv("XDG_CURRENT_DESKTOP", "").lower()
            match desktop_env:
                case "cinnamon" | "x-cinnamon" | "cinnamon-session" | "cinnamon2d":
                    os.system(
                        f"gsettings set org.cinnamon.desktop.background picture-uri file://{image_path}"
                    )

                case "gnome" | "ubuntu" | "gnome-session":
                    os.system(
                        f"gsettings set org.gnome.desktop.background picture-uri file://{image_path}"
                    )

                case "kde" | "plasma":
                    os.system(
                        f"qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
                        f'"var Desktops = desktops(); for (i=0; i<Desktops.length; i++) {{ Desktops[i].wallpaperPlugin = '
                        f"'org.kde.image'; Desktops[i].currentConfigGroup = Array('Wallpaper', 'org.kde.image', 'General'); "
                        f"Desktops[i].writeConfig('Image', '{image_path}'); }};"
                    )

                case "xfce":
                    os.system(
                        f'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-path -s file://{image_path}'
                    )

                case "lxqt":
                    os.system(f"pcmanfm --set-wallpaper {image_path}")

                case "mate":
                    os.system(
                        f"gsettings set org.mate.background picture-filename file://{image_path}"
                    )
                case _:
                    return False
        case _:
            return False
    return True


def get_file():
    match system:
        case "Windows":
            return filedialog.askopenfilename(
                filetypes=[('', '*.jpg;*.jpeg;*.png'), ('All Files', '*')]
            )
        case "Linux":
            return (
                os.popen(
                    "zenity --file-selection --file-filter='Image files (png, jpg, jpeg) | *.png *.jpg *.jpeg' --file-filter='All files | *'"
                )
                .read()
                .strip()
            )
        case _:
            return False
