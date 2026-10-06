"""Outline the official mark, with its acid symbol on a Kinq grey square."""
import argparse
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--font", type=Path, required=True, help="Official DM Sans variable font")
args = parser.parse_args()
font = TTFont(args.font)
font = instantiateVariableFont(font, {"opsz": 9, "wght": 800}, inplace=False)
glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
scale = 54 / font["head"].unitsPerEm
measure = ImageFont.truetype(str(args.font), 54 * 3)
measure.set_variation_by_axes([9, 800])
bounds = []
for char in "kinq":
    pen = BoundsPen(glyphs)
    glyphs[cmap[ord(char)]].draw(pen)
    bounds.append(pen.bounds)
low, high = min(b[1] for b in bounds), max(b[3] for b in bounds)
baseline = (64 + (high + low) * scale) / 2
width = math.ceil(55 + measure.getlength("kinq") / 3 - 2.8 * 3 + 2)
root = ET.parse(ROOT / "assets/kinq-symbol.svg").getroot()
symbol = root.find("{http://www.w3.org/2000/svg}path").attrib["d"]
paths = ['<rect x="0" y="8" width="48" height="48" rx="4" fill="#3b3d39"/>',
         f'<path d="{symbol}" fill="#b2ff1a" transform="translate(0 8) scale(.75)"/>']
for index, char in enumerate("kinq"):
    pen = SVGPathPen(glyphs)
    glyphs[cmap[ord(char)]].draw(pen)
    x = 55 + measure.getlength("kinq"[:index]) / 3 - index * 2.8
    paths.append(f'<path d="{pen.getCommands()}" fill="#171916" transform="translate({x:.4f} {baseline:.4f}) scale({scale:.6f} {-scale:.6f})"/>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="64" viewBox="0 0 {width} 64" role="img" aria-label="Kinq">'+''.join(paths)+'</svg>\n'
(ROOT / "assets/kinq-logo-print.svg").write_text(svg)
print(f"Transparent official wordmark: {width} x 64")
