"""PROTOTYPE — descartável. Sprites "pintados" (2.5D) a partir de silhuetas SVG.

Uso: python3 tools/art_prototype_painted/build.py   (requer Pillow, numpy, scipy e cairosvg)
Saída: tools/art_prototype_painted/out/

O SVG só define silhuetas e materiais. Cada filho direto de <g data-z="N"> é uma "peça":
  data-mat   cloth | skin | leather | metal | mail | wood | hair | glow | flat (padrão: cloth)
  data-vol   raio de arredondamento em unidades SVG (padrão 4)
  data-color cor base (@nome) quando a peça é um <g>; senão vale o fill
Para cada peça o build renderiza a máscara em alta resolução, gera um mapa de altura
(máscara borrada + textura do material), tira normais e ilumina: luz quente de cima/esquerda,
ambiente frio, especular/reflexo para metal, luz de borda fria à direita. Antes de pintar a
peça, projeta a sombra dela no que já está embaixo (sombra de contato). Sem contorno.
"""
import copy
import io
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import cairosvg
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, shift as nd_shift

ROOT = Path(__file__).parent
OUT = ROOT / "out"
SIZE = 160       # tamanho final do sprite
HI = 640         # resolução de trabalho
S = HI / SIZE    # pixels de trabalho por unidade SVG

PALETTE = {
    "void": "#0b0a0e", "shadow": "#1d1a22", "char": "#2a2530", "slate": "#3b3742",
    "bone": "#b8ab90", "bone_light": "#ddd3b8",
    "skin_dark": "#4a3530", "skin": "#8a6350", "skin_light": "#b08670", "pale": "#9a8a78",
    "hair": "#2a2224",
    "linen": "#5a5144", "cloth_dark": "#1f1d24", "cloth": "#34313b",
    "leather_dark": "#2a1c13", "leather": "#4a3423",
    "blood_dark": "#3a1216", "blood": "#5f1a1f",
    "iron_dark": "#2a2e35", "iron": "#4c525c", "iron_light": "#7d8590",
    "rust": "#6a3a22", "brass": "#8a6d33",
    "wood": "#4a3421", "wood_dark": "#2c1e13",
    "ember": "#ff7a2a", "frost": "#8cc8ff", "soul": "#4fe0b0",
    "rot": "#4d5540", "burnt": "#3a221b", "ice": "#4a6478",
}

LIGHT = np.array([-0.55, -0.7, 0.55])
LIGHT /= np.linalg.norm(LIGHT)
WARM = np.array([1.0, 0.86, 0.68])     # tocha
AMBIENT = np.array([0.42, 0.46, 0.58])  # ambiente frio
RIM = np.array([0.55, 0.75, 1.0])

# amb, difuso, especular, brilho (expoente), reflexo de ambiente, borda, amplitude da textura
MATERIALS = {
    "cloth":   dict(amb=0.55, diff=0.75, spec=0.0, shin=1, env=0.0, rim=0.35, tex=0.035),
    "skin":    dict(amb=0.6, diff=0.7, spec=0.12, shin=12, env=0.0, rim=0.45, tex=0.006),
    "leather": dict(amb=0.5, diff=0.75, spec=0.18, shin=10, env=0.0, rim=0.4, tex=0.01),
    "hair":    dict(amb=0.5, diff=0.7, spec=0.25, shin=20, env=0.0, rim=0.5, tex=0.06),
    "wood":    dict(amb=0.5, diff=0.75, spec=0.1, shin=8, env=0.0, rim=0.35, tex=0.05),
    "metal":   dict(amb=0.22, diff=0.5, spec=0.75, shin=36, env=0.45, rim=0.6, tex=0.02),
    "mail":    dict(amb=0.3, diff=0.6, spec=0.8, shin=14, env=0.5, rim=0.5, tex=0.12),
}


def hex_rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255


# ---------- leitura ----------

def load_part(name):
    text = (ROOT / "sprites" / f"{name}.svg").read_text()
    for local in re.findall(r'id="([\w-]+)"', text):
        text = text.replace(f'id="{local}"', f'id="{name}-{local}"').replace(f"url(#{local})", f"url(#{name}-{local})")
    root = ET.fromstring(f"<root>{text}</root>")
    defs, units = [], []
    for el in root:
        if el.tag == "defs":
            defs.extend(el)
            continue
        assert el.tag == "g" and "data-z" in el.attrib, f"{name}.svg: topo deve ser <defs> ou <g data-z>"
        z = int(el.attrib["data-z"])
        units.extend((z, child) for child in el)
    return defs, units


def resolve(text, swap):
    def color(m):
        n = m.group(1)
        assert n in PALETTE, f"cor fora da paleta: {n}"
        return PALETTE[swap.get(n, n)]
    return re.sub(r"@([a-z_]+)", color, text)


def svg_doc(defs, el, swap, wrapper):
    body = "".join(ET.tostring(d, encoding="unicode") for d in defs) + ET.tostring(el, encoding="unicode")
    return resolve(f'<svg xmlns="http://www.w3.org/2000/svg" width="{HI}" height="{HI}" viewBox="0 0 {SIZE} {SIZE}">'
                   f'<g {wrapper}>{body}</g></svg>', swap)


def rasterize(svg):
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=HI, output_height=HI)
    return np.asarray(Image.open(io.BytesIO(png)).convert("RGBA")).astype(np.float32) / 255


def as_mask(el):
    el = copy.deepcopy(el)
    for node in el.iter():
        if node.get("fill", "") != "none":
            node.set("fill", "#fff")
        if node.get("stroke") not in (None, "none"):
            node.set("stroke", "#fff")
        node.attrib.pop("opacity", None)
    return el


# ---------- texturas ----------

def texture(mat, seed):
    rng = np.random.default_rng(seed)
    if mat in ("wood", "hair"):
        n = rng.normal(0, 1, (HI // (24 if mat == "wood" else 40), HI))
        n = np.asarray(Image.fromarray(n.astype(np.float32), "F").resize((HI, HI), Image.BICUBIC))
        return gaussian_filter(n, (0, 0.8))
    if mat == "mail":
        yy, xx = np.mgrid[0:HI, 0:HI]
        return np.sin(xx * 1.1 + (yy // 4 % 2) * 1.5) * np.sin(yy * 0.8)
    if mat == "metal":
        n = gaussian_filter(rng.normal(0, 1, (HI, HI)), 10) * 2.5
        scratches = np.zeros((HI, HI), np.float32)
        for _ in range(60):
            x, y = rng.integers(0, HI, 2)
            ang, length = rng.uniform(0, np.pi), rng.integers(4, 14)
            for t in range(length):
                xi, yi = int(x + t * np.cos(ang)), int(y + t * np.sin(ang))
                if 0 <= xi < HI and 0 <= yi < HI:
                    scratches[yi, xi] = -0.6
        return n + gaussian_filter(scratches, 0.6)
    if mat == "cloth":
        return gaussian_filter(rng.normal(0, 1, (HI, HI)), 9) * 6 + gaussian_filter(rng.normal(0, 0.25, (HI, HI)), 0.7)
    return gaussian_filter(rng.normal(0, 1, (HI, HI)), 1.2)


TEX_CACHE = {}


def tex(mat, seed=3):
    key = (mat, seed)
    if key not in TEX_CACHE:
        TEX_CACHE[key] = texture(mat, seed).astype(np.float32)
    return TEX_CACHE[key]


# ---------- iluminação ----------

def shade(mask, base, mat, vol):
    p = MATERIALS[mat]
    r = max(1.0, vol * S)
    h = np.sqrt(np.clip(gaussian_filter(mask, r), 0, 1))
    h = h + tex(mat) * p["tex"] * mask
    gy, gx = np.gradient(h)
    k = r * 1.6
    n = np.dstack([-gx * k, -gy * k, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    ndl = np.clip(n @ LIGHT, 0, 1)[..., None]
    half = LIGHT + np.array([0, 0, 1.0])
    half /= np.linalg.norm(half)
    spec = np.clip(n @ half, 0, 1) ** p["shin"]
    color = base * (AMBIENT * p["amb"] + WARM * ndl * p["diff"])
    if mat == "skin":  # sombra levemente avermelhada
        color += base * np.array([0.18, 0.04, 0.0]) * (1 - ndl)
    if p["env"]:  # reflexo falso: céu escuro em cima, chão quente embaixo, horizonte claro
        ry = n[..., 1:2]
        env = np.where(ry < 0, np.array([0.30, 0.32, 0.38]) * (1 + ry), np.array([0.35, 0.25, 0.18]) * (1 - ry))
        band = np.exp(-((ry + 0.15) ** 2) / 0.02) * np.array([0.5, 0.5, 0.55])
        color = color + (env + band) * p["env"] * (base * 1.6)
    color += WARM * spec[..., None] * p["spec"]
    rim = np.clip(n[..., 0], 0, 1) * (1 - n[..., 2]) ** 1.5
    color += RIM * rim[..., None] * p["rim"] * 0.6
    return np.clip(color, 0, 1)


def over(canvas, rgb, alpha):
    a = alpha[..., None]
    out_a = a + canvas[..., 3:4] * (1 - a)
    out_rgb = (rgb * a + canvas[..., :3] * canvas[..., 3:4] * (1 - a)) / np.maximum(out_a, 1e-6)
    canvas[..., :3], canvas[..., 3:4] = out_rgb, out_a


def compose(names, swap=None):
    swap = swap or {}
    defs, units = [], []
    for n in names:
        d, u = load_part(n)
        defs += d
        units += u
    units.sort(key=lambda u: u[0])
    canvas = np.zeros((HI, HI, 4), np.float32)
    glows = []
    for _, el in units:
        mat = el.get("data-mat", "cloth")
        if mat == "flat":
            img = rasterize(svg_doc(defs, el, swap, 'stroke="none"'))
            over(canvas, img[..., :3], img[..., 3])
            continue
        mask = rasterize(svg_doc(defs, as_mask(el), swap, 'fill="#fff" stroke="none"'))[..., 3]
        base = hex_rgb(resolve(el.get("data-color") or el.get("fill"), swap))
        if mat == "glow":
            over(canvas, np.clip(base * 1.3, 0, 1) * np.ones((HI, HI, 3)), mask)
            glows.append((mask, base))
            continue
        # sombra de contato no que já foi pintado
        sh = gaussian_filter(nd_shift(mask, (2.2 * S, 1.2 * S), order=1), 2.2 * S)
        canvas[..., :3] *= 1 - (np.clip(sh * 0.6, 0, 0.6) * (1 - mask))[..., None]
        over(canvas, shade(mask, base, mat, float(el.get("data-vol", 4))), mask)
    for mask, base in glows:  # brilho emissivo por cima de tudo
        g = gaussian_filter(mask, 6 * S) * 1.6
        canvas[..., :3] = np.clip(canvas[..., :3] + base * g[..., None] * 0.8, 0, 1)
        canvas[..., 3] = np.maximum(canvas[..., 3], np.clip(g * 0.7, 0, 1))
    return Image.fromarray((canvas * 255).astype(np.uint8), "RGBA")


def floor(size):
    yy, xx = np.mgrid[0:size, 0:size] / size
    light = np.clip(1.15 - 1.4 * np.hypot(xx - 0.45, yy - 0.7), 0.3, 1.0)
    tex_ = 1 + np.random.default_rng(1).normal(0, 0.05, (size, size))
    rgb = np.clip(np.array([62, 56, 60]) * (light * tex_)[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([rgb, np.full((size, size), 255, np.uint8)]), "RGBA")


def on_floor(img, size):
    bg = floor(size)
    bg.alpha_composite(img.resize((size, size), Image.LANCZOS))
    return bg


CUTS = {
    "hero_heavy_sword": (["body", "armor_heavy", "weapon_sword"], {}),
    "hero_none_sword": (["body", "weapon_sword"], {}),
    "ghoul_rot": (["ghoul"], {}),
    "ghoul_burnt": (["ghoul"], {"rot": "burnt"}),
    "ghoul_frost": (["ghoul"], {"rot": "ice", "ember": "frost"}),
}


def main():
    OUT.mkdir(exist_ok=True)
    finals = []
    for name, (parts, swap) in CUTS.items():
        img = compose(parts, swap)
        img.resize((SIZE, SIZE), Image.LANCZOS).save(OUT / f"{name}.png")
        finals.append(img)
    # prancha em tamanho real (160) e prancha ampliada (2x) dos três primeiros
    sheet = Image.new("RGBA", (6 + len(finals) * (SIZE + 6), SIZE + 12), PALETTE["void"])
    for i, img in enumerate(finals):
        sheet.alpha_composite(on_floor(img, SIZE), (6 + i * (SIZE + 6), 6))
    sheet.save(OUT / "preview.png")
    big = 2 * SIZE * 2
    zoom = Image.new("RGBA", (6 + 3 * (big + 6), big + 12), PALETTE["void"])
    for i, img in enumerate(finals[:3]):
        zoom.alpha_composite(on_floor(img, big), (6 + i * (big + 6), 6))
    zoom.save(OUT / "preview_zoom.png")
    print(f"ok: {len(finals)} sprites em {OUT}")


if __name__ == "__main__":
    main()
