"""PROTOTYPE — descartável. Sprites vetoriais (SVG) 160x160 com paper-doll e troca de paleta.

Uso: python3 tools/art_prototype_svg/build.py   (requer Pillow e cairosvg)
Saída: tools/art_prototype_svg/out/  (.svg importável no Godot + .png renderizado)

Cada peça em sprites/*.svg é um fragmento com grupos <g data-z="N">. O build empilha os
grupos por z, troca as cores "@nome" pela Endesga 32 (com troca de paleta opcional) e gera
os degradês de sombreamento em blocos (url(#r-RAMPA) radial, url(#l-RAMPA) linear).
"""
import io
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
OUT = ROOT / "out"
SIZE = 160

NAMES = [
    "rust", "clay", "sand", "skin_light", "skin_mid", "brown", "brown_dark", "red_dark",
    "red", "orange", "gold", "yellow", "green", "green_mid", "green_dark", "teal_dark",
    "blue_dark", "blue", "cyan", "white", "steel_light", "steel", "steel_dark", "navy",
    "navy_dark", "black", "crimson", "purple_dark", "purple", "pink", "peach", "tan",
]
HEX = (ROOT.parent / "art_prototype" / "endesga32.hex").read_text().split()
PALETTE = dict(zip(NAMES, ("#" + h for h in HEX)))

# rampa: (luz, base, sombra)
RAMPS = {
    "skin": ("peach", "skin_light", "skin_mid"),
    "hair": ("brown", "brown_dark", "black"),
    "tunic": ("steel_dark", "navy", "navy_dark"),
    "pants": ("tan", "skin_mid", "brown"),
    "boots": ("brown", "brown_dark", "black"),
    "belt": ("clay", "rust", "brown_dark"),
    "leather": ("tan", "skin_mid", "brown"),
    "mail": ("steel_light", "steel", "steel_dark"),
    "plate": ("white", "steel_light", "steel"),
    "gold": ("yellow", "gold", "orange"),
    "blade": ("white", "steel_light", "steel"),
    "wood": ("tan", "brown", "brown_dark"),
    "gem": ("white", "cyan", "blue"),
    "plume": ("pink", "red", "red_dark"),
    "gob": ("green", "green_mid", "green_dark"),
    "cloth": ("tan", "brown", "brown_dark"),
}


def defs(swap):
    c = lambda name: PALETTE[swap.get(name, name)]
    out = []
    for ramp, (light, base, shadow) in RAMPS.items():
        stops = [(0, light), (0.34, light), (0.34, base), (0.76, base), (0.76, shadow), (1, shadow)]
        s = "".join(f'<stop offset="{o}" stop-color="{c(n)}"/>' for o, n in stops)
        out.append(f'<radialGradient id="r-{ramp}" cx="0.3" cy="0.26" r="0.86">{s}</radialGradient>')
        out.append(f'<linearGradient id="l-{ramp}" x1="0" y1="0" x2="0.7" y2="1">{s}</linearGradient>')
    out.append(
        f'<pattern id="rings" width="6" height="5" patternUnits="userSpaceOnUse">'
        f'<path d="M0,2.5 a3,2.5 0 0 0 6,0" fill="none" stroke="{c("steel_dark")}" stroke-width="1"/></pattern>')
    return "<defs>" + "".join(out) + "</defs>"


def load_groups(name):
    text = (ROOT / "sprites" / f"{name}.svg").read_text()
    root = ET.fromstring(f"<root>{text}</root>")
    groups = []
    for g in root:
        assert g.tag == "g" and "data-z" in g.attrib, f"{name}.svg: todo bloco de topo deve ser <g data-z>"
        groups.append((int(g.attrib["data-z"]), ET.tostring(g, encoding="unicode")))
    return groups


def compose(names, swap=None):
    swap = swap or {}
    groups = sorted((g for n in names for g in load_groups(n)), key=lambda g: g[0])
    body = "".join(markup for _, markup in groups)

    def color(match):
        name = match.group(1)
        assert name in PALETTE, f"cor fora da paleta: {name}"
        return PALETTE[swap.get(name, name)]

    body = re.sub(r"@([a-z_]+)", color, body)
    for ramp in set(re.findall(r"url\(#[rl]-([a-z_]+)\)", body)):
        assert ramp in RAMPS, f"rampa desconhecida: {ramp}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">'
            f'{defs(swap)}<g stroke="{PALETTE["black"]}" stroke-width="3" stroke-linejoin="round" '
            f'stroke-linecap="round">{body}</g></svg>')


def render(svg, size=SIZE):
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")


ARMORS = [None, "armor_light", "armor_medium", "armor_heavy"]
WEAPONS = [None, "weapon_sword", "weapon_axe", "weapon_bow", "weapon_staff"]

GOBLIN_VARIANTS = {
    "normal": {},
    "fire": {"green": "orange", "green_mid": "red", "green_dark": "red_dark"},
    "frost": {"green": "cyan", "green_mid": "blue", "green_dark": "blue_dark", "yellow": "white"},
}


def sheet(rows, pad=6):
    cols = max(len(r) for r in rows)
    img = Image.new("RGBA", (pad + cols * (SIZE + pad), pad + len(rows) * (SIZE + pad)), PALETTE["navy_dark"])
    draw = ImageDraw.Draw(img)
    for r, row in enumerate(rows):
        for c, sprite in enumerate(row):
            x, y = pad + c * (SIZE + pad), pad + r * (SIZE + pad)
            draw.rectangle([x, y, x + SIZE - 1, y + SIZE - 1], fill=PALETTE["sand"])
            img.alpha_composite(sprite, (x, y))
    return img


def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    for armor in ARMORS:
        row = []
        for weapon in WEAPONS:
            svg = compose(["body"] + [s for s in (armor, weapon) if s])
            name = f"hero_{(armor or 'armor_none').split('_')[1]}_{(weapon or 'weapon_none').split('_')[1]}"
            (OUT / f"{name}.svg").write_text(svg)
            img = render(svg)
            img.save(OUT / f"{name}.png")
            row.append(img)
        rows.append(row)
    goblins = []
    for variant, swap in GOBLIN_VARIANTS.items():
        svg = compose(["goblin"], swap)
        (OUT / f"goblin_{variant}.svg").write_text(svg)
        img = render(svg)
        img.save(OUT / f"goblin_{variant}.png")
        goblins.append(img)
    sheet(rows + [goblins]).save(OUT / "preview.png")
    # o mesmo vetor em 3x, para mostrar que escala sem perder nitidez
    zoom = Image.new("RGBA", (SIZE * 3 * 2, SIZE * 3), PALETTE["sand"])
    zoom.alpha_composite(render(compose(["body", "armor_heavy", "weapon_sword"]), SIZE * 3), (0, 0))
    zoom.alpha_composite(render(compose(["goblin"]), SIZE * 3), (SIZE * 3, 0))
    zoom.save(OUT / "preview_zoom.png")
    print(f"ok: {len(ARMORS) * len(WEAPONS) + len(goblins)} sprites (.svg + .png) + previews em {OUT}")


if __name__ == "__main__":
    main()
