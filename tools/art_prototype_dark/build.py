"""PROTOTYPE — descartável. Sprites SVG 160x160 em estilo sombrio (dark fantasy), com paper-doll.

Uso: python3 tools/art_prototype_dark/build.py   (requer Pillow, numpy e cairosvg)
Saída: tools/art_prototype_dark/out/

Cada peça em sprites/*.svg tem grupos <g data-z="N"> e, opcionalmente, <defs> próprios
(clipPaths etc.; os ids são prefixados com o nome da peça para não colidir).
Cores "@nome" vêm de PALETTE; degradês suaves gerados por rampa:
  url(#s-RAMPA) radial (volume), url(#v-RAMPA) diagonal, url(#h-RAMPA) cilindro horizontal.
Depois de renderizar, aplica granulado determinístico só onde há pixel.
"""
import io
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import cairosvg
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
OUT = ROOT / "out"
SIZE = 160

PALETTE = {
    "void": "#0b0a0e", "outline": "#120f14", "shadow": "#1d1a22", "char": "#2a2530", "slate": "#3b3742",
    "ash": "#57525c", "smoke": "#7c7680", "bone": "#b8ab90", "bone_light": "#ddd3b8",
    "skin_dark": "#4a3530", "skin": "#7d5a4a", "skin_light": "#b08670",
    "hair_dark": "#141114", "hair": "#2e2528", "hair_light": "#4a3d3e",
    "linen_dark": "#2f2a25", "linen": "#4f473c", "linen_light": "#776b59",
    "cloth_dark": "#1c1a20", "cloth": "#2f2c35", "cloth_light": "#4a4652",
    "leather_dark": "#21160f", "leather": "#43301f", "leather_light": "#6e4f35",
    "blood_dark": "#2a0d10", "blood": "#5a181d", "blood_light": "#8f2b2c",
    "iron_dark": "#1f2228", "iron": "#41464f", "iron_light": "#737b86", "iron_shine": "#c4cad1",
    "rust": "#5e3220", "rust_light": "#94512c",
    "brass_dark": "#3f3017", "brass": "#82662e", "brass_light": "#c7a35a",
    "wood_dark": "#1f150d", "wood": "#45311f", "wood_light": "#6b5034",
    "ember": "#e0702a", "ember_light": "#ffc46b",
    "frost": "#7fb0cf", "frost_light": "#d6f0ff",
    "soul_dark": "#173f3a", "soul": "#38b896", "soul_light": "#c2ffe9",
    "rot_dark": "#20241c", "rot": "#454d3a", "rot_light": "#717a5e",
    "burnt_dark": "#140c0a", "burnt": "#3a2018", "burnt_light": "#7a3a22",
    "ice_dark": "#1a2633", "ice": "#3d5a70", "ice_light": "#8db2c9",
}

# rampa: (sombra, meio, luz)
RAMPS = {
    "skin": ("skin_dark", "skin", "skin_light"),
    "hair": ("hair_dark", "hair", "hair_light"),
    "linen": ("linen_dark", "linen", "linen_light"),
    "cloth": ("cloth_dark", "cloth", "cloth_light"),
    "leather": ("leather_dark", "leather", "leather_light"),
    "blood": ("blood_dark", "blood", "blood_light"),
    "iron": ("iron_dark", "iron", "iron_light"),
    "steel": ("iron", "iron_light", "iron_shine"),
    "brass": ("brass_dark", "brass", "brass_light"),
    "wood": ("wood_dark", "wood", "wood_light"),
    "bone": ("linen", "bone", "bone_light"),
    "soul": ("soul_dark", "soul", "soul_light"),
    "rot": ("rot_dark", "rot", "rot_light"),
}


def defs(swap):
    c = lambda name: PALETTE[swap.get(name, name)]
    out = []
    for ramp, (dark, mid, light) in RAMPS.items():
        soft = f'<stop offset="0" stop-color="{c(light)}"/><stop offset="0.5" stop-color="{c(mid)}"/>' \
               f'<stop offset="1" stop-color="{c(dark)}"/>'
        cyl = f'<stop offset="0" stop-color="{c(mid)}"/><stop offset="0.3" stop-color="{c(light)}"/>' \
              f'<stop offset="0.65" stop-color="{c(mid)}"/><stop offset="1" stop-color="{c(dark)}"/>'
        out.append(f'<radialGradient id="s-{ramp}" cx="0.32" cy="0.28" r="0.85">{soft}</radialGradient>')
        out.append(f'<linearGradient id="v-{ramp}" x1="0.15" y1="0" x2="0.85" y2="1">{soft}</linearGradient>')
        out.append(f'<linearGradient id="h-{ramp}" x1="0" y1="0" x2="1" y2="0">{cyl}</linearGradient>')
    out.append(f'<radialGradient id="glow-ember"><stop offset="0" stop-color="{c("ember_light")}" stop-opacity="0.9"/>'
               f'<stop offset="0.4" stop-color="{c("ember")}" stop-opacity="0.45"/>'
               f'<stop offset="1" stop-color="{c("ember")}" stop-opacity="0"/></radialGradient>')
    out.append(f'<radialGradient id="glow-soul"><stop offset="0" stop-color="{c("soul_light")}" stop-opacity="0.8"/>'
               f'<stop offset="0.45" stop-color="{c("soul")}" stop-opacity="0.35"/>'
               f'<stop offset="1" stop-color="{c("soul")}" stop-opacity="0"/></radialGradient>')
    out.append(f'<pattern id="rings" width="4" height="3.4" patternUnits="userSpaceOnUse">'
               f'<path d="M0,1.7 a2,1.7 0 0 0 4,0" fill="none" stroke="{c("iron_dark")}" stroke-width="0.8"/>'
               f'<circle cx="2" cy="0.6" r="0.5" fill="{c("iron_light")}" opacity="0.5"/></pattern>')
    return "".join(out)


def load_part(name):
    text = (ROOT / "sprites" / f"{name}.svg").read_text()
    for local in re.findall(r'id="([\w-]+)"', text):
        text = text.replace(f'id="{local}"', f'id="{name}-{local}"').replace(f"url(#{local})", f"url(#{name}-{local})")
    root = ET.fromstring(f"<root>{text}</root>")
    local_defs, groups = [], []
    for el in root:
        if el.tag == "defs":
            local_defs.extend(ET.tostring(child, encoding="unicode") for child in el)
        else:
            assert el.tag == "g" and "data-z" in el.attrib, f"{name}.svg: topo deve ser <defs> ou <g data-z>"
            groups.append((int(el.attrib["data-z"]), ET.tostring(el, encoding="unicode")))
    return local_defs, groups


def compose(names, swap=None):
    swap = swap or {}
    all_defs, groups = [], []
    for n in names:
        d, g = load_part(n)
        all_defs += d
        groups += g
    body = "".join(markup for _, markup in sorted(groups, key=lambda g: g[0]))
    markup = "<defs>" + "".join(all_defs) + "</defs>" + body

    def color(match):
        name = match.group(1)
        assert name in PALETTE, f"cor fora da paleta: {name}"
        return PALETTE[swap.get(name, name)]

    markup = re.sub(r"@([a-z_]+)", color, markup)
    for ramp in set(re.findall(r"url\(#[svh]-([a-z_]+)\)", markup)):
        assert ramp in RAMPS, f"rampa desconhecida: {ramp}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">'
            f'<defs>{defs(swap)}</defs><g stroke="{PALETTE["outline"]}" stroke-width="1.4" '
            f'stroke-linejoin="round" stroke-linecap="round">{markup}</g></svg>')


def render(svg, size=SIZE, grain=0.07, seed=7):
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    img = np.asarray(Image.open(io.BytesIO(png)).convert("RGBA")).astype(np.float32)
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, grain, img.shape[:2])[..., None]
    img[..., :3] = np.clip(img[..., :3] * (1 + noise), 0, 255)
    return Image.fromarray(img.astype(np.uint8), "RGBA")


ARMORS = [None, "armor_light", "armor_medium", "armor_heavy"]
WEAPONS = ["weapon_sword", "weapon_axe", "weapon_bow", "weapon_staff"]

GHOUL_VARIANTS = {
    "rot": {},
    "burnt": {"rot_dark": "burnt_dark", "rot": "burnt", "rot_light": "burnt_light"},
    "frost": {"rot_dark": "ice_dark", "rot": "ice", "rot_light": "ice_light",
              "ember": "frost", "ember_light": "frost_light"},
}


def floor_tile(size):
    """Piso de pedra escuro com luz de tocha no centro, só para a prancha."""
    yy, xx = np.mgrid[0:size, 0:size] / size
    light = np.clip(1.1 - 1.3 * np.hypot(xx - 0.5, yy - 0.62), 0.35, 1.0)
    base = np.array([66, 60, 70], np.float32)
    rng = np.random.default_rng(1)
    tex = 1 + rng.normal(0, 0.05, (size, size))
    rgb = np.clip(base * (light * tex)[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([rgb, np.full((size, size), 255, np.uint8)]), "RGBA")


def sheet(rows, pad=6):
    cols = max(len(r) for r in rows)
    img = Image.new("RGBA", (pad + cols * (SIZE + pad), pad + len(rows) * (SIZE + pad)), PALETTE["void"])
    tile = floor_tile(SIZE)
    for r, row in enumerate(rows):
        for c, sprite in enumerate(row):
            x, y = pad + c * (SIZE + pad), pad + r * (SIZE + pad)
            img.alpha_composite(tile, (x, y))
            img.alpha_composite(sprite, (x, y))
    return img


def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    for armor in ARMORS:
        row = []
        for weapon in WEAPONS:
            svg = compose(["body"] + [s for s in (armor, weapon) if s])
            name = f"hero_{(armor or 'armor_none').split('_')[1]}_{weapon.split('_')[1]}"
            (OUT / f"{name}.svg").write_text(svg)
            img = render(svg)
            img.save(OUT / f"{name}.png")
            row.append(img)
        rows.append(row)
    ghouls = []
    for variant, swap in GHOUL_VARIANTS.items():
        svg = compose(["ghoul"], swap)
        (OUT / f"ghoul_{variant}.svg").write_text(svg)
        img = render(svg)
        img.save(OUT / f"ghoul_{variant}.png")
        ghouls.append(img)
    sheet(rows + [ghouls]).save(OUT / "preview.png")

    big = SIZE * 3
    zoom = Image.new("RGBA", (big * 3, big), PALETTE["void"])
    picks = [["body", "armor_heavy", "weapon_sword"], ["body", "armor_light", "weapon_bow"], ["ghoul"]]
    tile = floor_tile(big)
    for i, parts in enumerate(picks):
        zoom.alpha_composite(tile, (i * big, 0))
        zoom.alpha_composite(render(compose(parts), big, grain=0.05), (i * big, 0))
    zoom.save(OUT / "preview_zoom.png")
    print(f"ok: {len(ARMORS) * len(WEAPONS) + len(ghouls)} sprites + previews em {OUT}")


if __name__ == "__main__":
    main()
