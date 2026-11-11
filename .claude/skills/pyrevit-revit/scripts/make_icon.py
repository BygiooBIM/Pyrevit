"""Genera un icon.png (96x96) simple para un botón pyRevit.

Uso: python make_icon.py <carpeta.pushbutton> "TXT" "#1f6feb"
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont


def main():
    folder, text = sys.argv[1], sys.argv[2]
    color = sys.argv[3] if len(sys.argv) > 3 else "#1f6feb"
    size = 96
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([4, 4, size - 4, size - 4], radius=18, fill=color)
    font = None
    for name in ("DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf"):
        try:
            font = ImageFont.truetype(name, 40 if len(text) <= 2 else 28)
            break
        except OSError:
            continue
    font = font or ImageFont.load_default()
    box = d.textbbox((0, 0), text, font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    d.text(((size - w) / 2 - box[0], (size - h) / 2 - box[1]), text, fill="white", font=font)
    img.save(os.path.join(folder, "icon.png"))


if __name__ == "__main__":
    main()
