import threading
from PIL import Image, ImageDraw
import pystray


def _create_icon_image():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 60, 60], fill=(80, 160, 255, 230))
    draw.text((20, 18), "S", fill=(255, 255, 255, 255))
    return img


def run_tray(on_show, on_quit):
    icon = pystray.Icon(
        name="skuldop",
        icon=_create_icon_image(),
        title="オペレーションスクルド",
        menu=pystray.Menu(
            pystray.MenuItem("開く", lambda icon, item: on_show(), default=True),
            pystray.MenuItem("終了", lambda icon, item: on_quit(icon)),
        ),
    )
    icon.run()


def start_tray(on_show, on_quit):
    t = threading.Thread(target=run_tray, args=(on_show, on_quit), daemon=True)
    t.start()
