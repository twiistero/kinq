"""Export native KINQ Brand to a transparent PNG with bundled Python / Pillow."""
from pathlib import Path
import math
import re
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCALE = 3
SYMBOL_SIZE, GAP, FONT_SIZE, TRACKING = 48, 7, 54, -2.8


def build():
    # Brand(size: 48): same official source, native font, weight, gap and tracking.
    font = ImageFont.truetype(str(ROOT / "ios/KINQ/Resources/Fonts/DMSans.ttf"), FONT_SIZE * SCALE)
    font.set_variation_by_axes([9, 800])
    symbol = ET.parse(ROOT / "assets/kinq-symbol.svg").getroot()
    path = symbol.find("{http://www.w3.org/2000/svg}path").attrib["d"]
    if re.search(r"[^MLZmlz\d\s.,-]", path):
        raise ValueError("Official symbol path changed; use a full SVG renderer")
    values = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", path)]
    coordinates = list(zip(values[::2], values[1::2]))
    height = 64 * SCALE
    word_width = font.getlength("kinq") + 3 * TRACKING * SCALE
    width = math.ceil((SYMBOL_SIZE + GAP) * SCALE + word_width + 2 * SCALE)
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    top = (height - SYMBOL_SIZE * SCALE) / 2
    draw.polygon([(x / 64 * SYMBOL_SIZE * SCALE, top + y / 64 * SYMBOL_SIZE * SCALE)
                  for x, y in coordinates], fill="#b2ff1a")
    bounds = font.getbbox("kinq")
    y = (height - (bounds[3] - bounds[1])) / 2 - bounds[1]
    for i, character in enumerate("kinq"):
        x = (SYMBOL_SIZE + GAP) * SCALE + font.getlength("kinq"[:i]) + i * TRACKING * SCALE
        draw.text((x, y), character, font=font, fill="#f4f4ee")
    output = ROOT / "backend/app/templates/kinq-logo.png"
    image.save(output, optimize=True)
    print(f"Official native logo exported: {width} x {height} pixels")


if __name__ == "__main__":
    build()
