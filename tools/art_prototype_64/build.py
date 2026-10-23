"""PROTOTYPE — descartável. Pixel art 64x64 gerada a partir de formas descritas em texto.

Uso: python3 tools/art_prototype_64/build.py
Saída: tools/art_prototype_64/out/

Pipeline: formas (elipse, cápsula, polígono, retângulo) -> rasterização sem antialias
-> sombreamento por rampa de cores (luz no canto superior esquerdo) -> linhas internas
entre peças -> contorno externo -> troca de paleta opcional -> PNG.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
OUT = ROOT / "out"
CELL = 64

NAMES = [
    "rust", "clay", "sand", "skin_light", "skin_mid", "brown", "brown_dark", "red_dark",
    "red", "orange", "gold", "yellow", "green", "green_mid", "green_dark", "teal_dark",
    "blue_dark", "blue", "cyan", "white", "steel_light", "steel", "steel_dark", "navy",
    "navy_dark", "black", "crimson", "purple_dark", "purple", "pink", "peach", "tan",
]
HEX = (ROOT.parent / "art_prototype" / "endesga32.hex").read_text().split()
PALETTE = {name: tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,) for name, h in zip(NAMES, HEX)}

LIGHT = (-0.45, -0.6, 0.66)
_n = math.sqrt(sum(c * c for c in LIGHT))
LIGHT = tuple(c / _n for c in LIGHT)
OUTLINE = "black"


# ---------- formas: cada uma devolve a normal (nx, ny, nz) no ponto, ou None se estiver fora ----------

def dome(dx, dy, flatten=1.0):
    d2 = dx * dx + dy * dy
    if d2 > 1:
        d2 = 1
    return dx * flatten, dy * flatten, math.sqrt(1 - d2)


def ellipse(cx, cy, rx, ry):
    def f(x, y):
        dx, dy = (x - cx) / rx, (y - cy) / ry
        return dome(dx, dy) if dx * dx + dy * dy <= 1 else None
    return f, (cx - rx, cy - ry, cx + rx, cy + ry)


def capsule(x1, y1, x2, y2, r):
    vx, vy = x2 - x1, y2 - y1
    length2 = vx * vx + vy * vy or 1e-9

    def f(x, y):
        t = max(0.0, min(1.0, ((x - x1) * vx + (y - y1) * vy) / length2))
        dx, dy = (x - (x1 + t * vx)) / r, (y - (y1 + t * vy)) / r
        return dome(dx, dy) if dx * dx + dy * dy <= 1 else None
    return f, (min(x1, x2) - r, min(y1, y2) - r, max(x1, x2) + r, max(y1, y2) + r)


def poly(points):
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    hw, hh = (max(xs) - min(xs)) / 2 or 1, (max(ys) - min(ys)) / 2 or 1

    def inside(x, y):
        hit = False
        j = len(points) - 1
        for i, (xi, yi) in enumerate(points):
            xj, yj = points[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                hit = not hit
            j = i
        return hit

    def f(x, y):
        return dome((x - cx) / hw, (y - cy) / hh, 0.7) if inside(x, y) else None
    return f, (min(xs), min(ys), max(xs), max(ys))


def rect(x, y, w, h):
    return poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])


SHAPES = {"ellipse": (ellipse, 4), "capsule": (capsule, 5), "rect": (rect, 4)}


# ---------- leitura do formato de texto ----------

def load_sprite(name):
    """Devolve (rampas, camadas). Cada camada: {z, ops}; op = forma sombreada ou detalhe de cor fixa."""
    path = ROOT / "sprites" / f"{name}.txt"
    ramps, layers = {}, []
    for n, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        cmd, *args = line.split()
        opts = dict(a.split("=", 1) for a in args if "=" in a)
        args = [a for a in args if "=" not in a]
        where = f"{path.name}:{n}"
        if cmd == "ramp":
            for c in args[1:]:
                assert c in PALETTE, f"{where} cor fora da paleta: {c}"
            ramps[args[0]] = args[1:]
        elif cmd == "layer":
            layers.append({"name": args[0], "z": int(opts.get("z", 0)), "ops": []})
        elif cmd in SHAPES or cmd == "poly":
            if cmd == "poly":
                ramp, pts = args[0], [tuple(map(float, p.split(","))) for p in args[1:]]
                shape = poly(pts)
            else:
                ctor, argc = SHAPES[cmd]
                shape, ramp = ctor(*map(float, args[:argc])), args[argc]
            assert ramp in ramps, f"{where} rampa desconhecida: {ramp}"
            layers[-1]["ops"].append(("shape", shape, ramps[ramp], opts, where))
        elif cmd in ("dot", "line", "box"):
            color = args[-1]
            assert color in PALETTE, f"{where} cor fora da paleta: {color}"
            layers[-1]["ops"].append((cmd, list(map(float, args[:-1])), color, where))
        else:
            raise AssertionError(f"{where} comando desconhecido: {cmd}")
    return layers


# ---------- composição ----------

def shade_index(normal, ramp_len, flat, pattern, x, y, soft=1.0):
    if flat is not None:
        idx = int(flat)
    else:
        nx, ny, nz = normal
        normal = (nx * soft, ny * soft, math.sqrt(max(0.0, 1 - soft * soft * (1 - nz * nz))))
        s = sum(a * b for a, b in zip(normal, LIGHT))
        t = max(0.0, min(1.0, (s + 0.2) / 1.2))
        idx = min(ramp_len - 1, int((1 - t) * ramp_len))
    if pattern == "mail" and y % 2 == 0 and (x // 2 + y // 2) % 2 == 0:
        idx = min(ramp_len - 1, idx + 1)
    if pattern == "grain" and (x * 7 + y * 3) % 11 == 0:
        idx = min(ramp_len - 1, idx + 1)
    return idx


def compose(sprite_names, swap=None):
    swap = swap or {}
    layers = sorted((layer for name in sprite_names for layer in load_sprite(name)), key=lambda layer: layer["z"])
    color = [[None] * CELL for _ in range(CELL)]
    part = [[None] * CELL for _ in range(CELL)]  # (ordem, camada, grupo) de quem pintou o pixel
    dark = {}  # parte -> cor mais escura da rampa (linha interna)
    order = 0
    for li, layer in enumerate(layers):
        for op in layer["ops"]:
            order += 1
            if op[0] == "shape":
                (fn, (x0, y0, x1, y1)), ramp, opts, where = op[1], op[2], op[3], op[4]
                key = (order, li, opts.get("group", f"#{order}"))
                if "group" in opts:  # formas do mesmo grupo dividem a mesma ordem
                    key = (dark_order(dark, li, opts["group"], order), li, opts["group"])
                dark[key] = ramp[-1]
                clip = float(opts["clip"]) if "clip" in opts else None
                for y in range(max(0, int(y0) - 1), min(CELL, int(y1) + 2)):
                    if clip is not None and y > clip:
                        continue
                    for x in range(max(0, int(x0) - 1), min(CELL, int(x1) + 2)):
                        normal = fn(x + 0.5, y + 0.5)
                        if normal is None:
                            continue
                        idx = shade_index(normal, len(ramp), opts.get("flat"), opts.get("pattern"), x, y,
                                          float(opts.get("soft", 1.0)))
                        color[y][x] = ramp[idx]
                        part[y][x] = key
            else:
                kind, nums, c, where = op
                if kind == "dot":
                    pixels = [(int(nums[0]), int(nums[1]))]
                elif kind == "box":
                    x, y, w, h = map(int, nums)
                    pixels = [(i, j) for j in range(y, y + h) for i in range(x, x + w)]
                else:
                    x1, y1, x2, y2 = nums
                    steps = int(max(abs(x2 - x1), abs(y2 - y1))) + 1
                    pixels = [(round(x1 + (x2 - x1) * k / max(1, steps - 1)), round(y1 + (y2 - y1) * k / max(1, steps - 1)))
                              for k in range(steps)]
                for x, y in pixels:
                    if 0 <= x < CELL and 0 <= y < CELL:
                        color[y][x] = c
                        part[y][x] = ("detail",)

    # linhas internas: na borda da peça de cima, onde encosta numa peça desenhada antes
    lines = []
    for y in range(CELL):
        for x in range(CELL):
            p = part[y][x]
            if not p or p[0] == "detail":
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < CELL and 0 <= ny < CELL):
                    continue
                q = part[ny][nx]
                if q and q[0] != "detail" and q != p and q[0] < p[0]:
                    lines.append((x, y, OUTLINE if q[1] != p[1] else dark[p]))
                    break
    for x, y, c in lines:
        color[y][x] = c

    # contorno externo
    outline = [(x, y) for y in range(CELL) for x in range(CELL) if color[y][x] is None and any(
        0 <= x + dx < CELL and 0 <= y + dy < CELL and color[y + dy][x + dx] is not None
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in outline:
        color[y][x] = OUTLINE

    img = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    for y in range(CELL):
        for x in range(CELL):
            if color[y][x]:
                img.putpixel((x, y), PALETTE[swap.get(color[y][x], color[y][x])])
    return img


def dark_order(dark, li, group, order):
    for key in dark:
        if key[1] == li and key[2] == group:
            return key[0]
    return order


ARMORS = [None, "armor_light", "armor_medium", "armor_heavy"]
WEAPONS = [None, "weapon_sword", "weapon_axe", "weapon_bow", "weapon_staff"]

GOBLIN_VARIANTS = {
    "normal": {},
    "fire": {"green": "orange", "green_mid": "red", "green_dark": "red_dark", "teal_dark": "purple_dark"},
    "frost": {"green": "cyan", "green_mid": "blue", "green_dark": "blue_dark", "teal_dark": "navy",
              "yellow": "white"},
}


def preview(rows, scale=4, pad=6):
    cols = max(len(r) for r in rows)
    size = CELL * scale
    sheet = Image.new("RGBA", (pad + cols * (size + pad), pad + len(rows) * (size + pad)), PALETTE["navy_dark"])
    draw = ImageDraw.Draw(sheet)
    for r, row in enumerate(rows):
        for c, img in enumerate(row):
            x, y = pad + c * (size + pad), pad + r * (size + pad)
            draw.rectangle([x, y, x + size - 1, y + size - 1], fill=PALETTE["sand"])
            sheet.alpha_composite(img.resize((size, size), Image.NEAREST), (x, y))
    return sheet


def main():
    OUT.mkdir(exist_ok=True)
    hero_rows = []
    for armor in ARMORS:
        row = []
        for weapon in WEAPONS:
            img = compose(["body"] + [s for s in (armor, weapon) if s])
            name = f"hero_{(armor or 'armor_none').split('_')[1]}_{(weapon or 'weapon_none').split('_')[1]}"
            img.save(OUT / f"{name}.png")
            row.append(img)
        hero_rows.append(row)
    goblins = []
    for variant, swap in GOBLIN_VARIANTS.items():
        img = compose(["goblin"], swap)
        img.save(OUT / f"goblin_{variant}.png")
        goblins.append(img)
    preview(hero_rows + [goblins]).save(OUT / "preview.png")
    print(f"ok: {len(ARMORS) * len(WEAPONS) + len(goblins)} sprites + preview.png em {OUT}")


if __name__ == "__main__":
    main()
