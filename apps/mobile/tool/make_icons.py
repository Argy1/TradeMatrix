"""Draws the app icon (the 3D logo tile from lib/widgets/brand.dart) and writes every size
Android, iOS and the web preview need.

Run from apps/mobile:  uv run --with pillow python tool/make_icons.py

Why a script: the logo is plain geometry (a gradient tile with a grid, a hard shadow and a
glow), so drawing it in code keeps the icon identical to the logo inside the app and makes it
easy to change later. Everything is drawn 4x too large and scaled down, which smooths the edges.
"""

import json
import pathlib
import re

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
BG = (6, 9, 19, 255)  # Tm.bg, the app's background
CYAN = (106, 228, 255)
VIOLET = (124, 92, 255)
SHADOW = (59, 47, 168, 255)  # the hard "3D" edge under the tile
SS = 4  # supersampling factor


def rounded_mask(size: int, radius: float) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
    return mask


def tile(size: int) -> Image.Image:
    """The logo face: cyan to violet from top-left to bottom-right, a 4 x 4 grid, a lit top edge."""
    # A diagonal gradient is the average of a left-to-right and a top-to-bottom one.
    down = Image.linear_gradient("L").resize((size, size))
    across = down.rotate(90)
    mix = ImageChops.add(across, down, scale=2)  # 0 at the top-left corner, 255 at the bottom-right
    cyan = Image.new("RGB", (size, size), CYAN)
    violet = Image.new("RGB", (size, size), VIOLET)
    face = Image.composite(violet, cyan, mix).convert("RGBA")

    lines = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(lines)
    width = max(1, round(size / 36))
    for i in range(5):
        at = round(i * (size - 1) / 4)
        draw.line((at, 0, at, size), fill=(255, 255, 255, 97), width=width)
        draw.line((0, at, size, at), fill=(255, 255, 255, 97), width=width)
    draw.rectangle((0, 0, size, round(size / 18)), fill=(255, 255, 255, 140))
    face = Image.alpha_composite(face, lines)
    face.putalpha(rounded_mask(size, size * 0.30))
    return face


def compose(canvas: int, tile_part: float, background: tuple | None, corner: float = 0.0) -> Image.Image:
    """The tile with its shadow and glow, centred on a square canvas.

    tile_part: tile width as a part of the canvas. background None keeps the canvas transparent.
    corner: rounds the canvas itself (used for the old-style Android icon).
    """
    big = canvas * SS
    size = round(big * tile_part)
    left = (big - size) // 2
    top = (big - size) // 2 - round(size / 24)  # lifted a little: the shadow sits below
    image = Image.new("RGBA", (big, big), background or (0, 0, 0, 0))

    # Soft violet glow under the tile.
    glow = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    glow_shape = Image.new("RGBA", (size, size), VIOLET + (128,))
    glow.paste(glow_shape, (left, top + round(size * 0.28)), rounded_mask(size, size * 0.30))
    image = Image.alpha_composite(image, glow.filter(ImageFilter.GaussianBlur(size / 4)))

    # Hard edge: the same shape, moved down. This is what makes the tile look thick.
    edge = Image.new("RGBA", (size, size), SHADOW)
    image.paste(edge, (left, top + round(size / 12)), rounded_mask(size, size * 0.30))

    face = tile(size)
    image.paste(face, (left, top), face)

    if corner:
        alpha = ImageChops.multiply(image.getchannel("A"), rounded_mask(big, big * corner))
        image.putalpha(alpha)
    return image.resize((canvas, canvas), Image.LANCZOS)


def save(image: Image.Image, path: pathlib.Path, opaque: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    (image.convert("RGB") if opaque else image).save(path, optimize=True)


def main() -> None:
    res = ROOT / "android/app/src/main/res"
    # Android. Phones since Android 8 use the "adaptive" icon: a foreground on a background,
    # cut to the phone's own shape. Only the middle 66 of 108 units is always visible.
    for name, scale in {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}.items():
        save(compose(round(108 * scale), 0.40, None), res / f"mipmap-{name}/ic_launcher_foreground.png")
        save(compose(round(48 * scale), 0.56, BG, corner=0.22), res / f"mipmap-{name}/ic_launcher.png")

    # iOS: every file listed in the asset catalog, at its own pixel size, without transparency.
    ios = ROOT / "ios/Runner/Assets.xcassets/AppIcon.appiconset"
    for entry in json.loads((ios / "Contents.json").read_text(encoding="utf-8"))["images"]:
        points = float(entry["size"].split("x")[0])
        pixels = round(points * int(re.sub(r"\D", "", entry["scale"])))
        save(compose(pixels, 0.56, BG), ios / entry["filename"], opaque=True)

    # Web preview. "Maskable" icons may be cut to a circle, so their tile is smaller.
    web = ROOT / "web"
    save(compose(32, 0.74, None), web / "favicon.png")
    for pixels in (192, 512):
        save(compose(pixels, 0.56, BG, corner=0.22), web / f"icons/Icon-{pixels}.png")
        save(compose(pixels, 0.44, BG), web / f"icons/Icon-maskable-{pixels}.png", opaque=True)

    # A large copy to look at (git-ignored build folder).
    save(compose(512, 0.56, BG, corner=0.22), ROOT / "build/icon_preview.png")
    print("icons written")


if __name__ == "__main__":
    main()
