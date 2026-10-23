"""PROTOTYPE — descartável. Gera PNGs de pixel art a partir de sprites em texto.

Uso: python3 tools/art_prototype/build.py
Saída: tools/art_prototype/out/
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
OUT = ROOT / "out"
CELL = 32

# Nomes para os 32 índices da Endesga 32 (ordem do arquivo .hex).
NAMES = [
    "rust", "clay", "sand", "skin_light", "skin_mid", "brown", "brown_dark", "red_dark",
    "red", "orange", "gold", "yellow", "green", "green_mid", "green_dark", "teal_dark",
    "blue_dark", "blue", "cyan", "white", "steel_light", "steel", "steel_dark", "navy",
    "navy_dark", "black", "crimson", "purple_dark", "purple", "pink", "peach", "tan",
]
HEX = (ROOT / "endesga32.hex").read_text().split()
assert len(HEX) == len(NAMES) == 32
PALETTE = {name: tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,) for name, h in zip(NAMES, HEX)}

DIRECTIVES = ("key", "layer")


def load_sprite(name):
    """Lê sprites/<name>.txt e devolve a lista de camadas: (z, x, y, linhas, chaves)."""
    path = ROOT / "sprites" / f"{name}.txt"
    keys, layers = {".": None}, []
    for n, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.split("#", 1)[0].rstrip()
        if not line:
            continue
        word = line.split()[0]
        if word == "key":
            _, char, color = line.split()
            assert color in PALETTE, f"{path}:{n} cor fora da paleta: {color}"
            keys[char] = color
        elif word == "layer":
            opts = dict(p.split("=") for p in line.split()[2:])
            x, y = map(int, opts.get("at", "0,0").split(","))
            layers.append({"name": line.split()[1], "z": int(opts.get("z", 0)), "x": x, "y": y, "rows": []})
        else:
            layer = layers[-1]
            if layer["rows"]:
                assert len(line) == len(layer["rows"][0]), f"{path}:{n} largura diferente das outras linhas"
            assert layer["x"] + len(line) <= CELL, f"{path}:{n} passa da borda"
            for char in line:
                assert char in keys, f"{path}:{n} caractere sem key: {char!r}"
            layer["rows"].append(line)
    for layer in layers:
        layer["keys"] = keys
    return layers


def compose(sprite_names, swap=None):
    """Empilha as camadas de vários sprites por z (paper-doll) e aplica troca de paleta."""
    swap = swap or {}
    layers = [layer for name in sprite_names for layer in load_sprite(name)]
    img = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    for layer in sorted(layers, key=lambda layer: layer["z"]):
        for dy, row in enumerate(layer["rows"]):
            for dx, char in enumerate(row):
                color = layer["keys"][char]
                if color:
                    img.putpixel((layer["x"] + dx, layer["y"] + dy), PALETTE[swap.get(color, color)])
    return img


ARMORS = [None, "armor_light", "armor_medium", "armor_heavy"]
WEAPONS = [None, "weapon_sword", "weapon_axe", "weapon_bow", "weapon_staff"]

GOBLIN_VARIANTS = {
    "normal": {},
    "fire": {"green": "red", "green_mid": "red_dark", "green_dark": "purple_dark"},
    "frost": {"green": "blue", "green_mid": "blue_dark", "green_dark": "navy", "yellow": "white"},
}


def preview(rows, scale=6, pad=4):
    """Prancha ampliada sobre um piso de areia, uma linha por grupo."""
    cols = max(len(r) for r in rows)
    size = CELL * scale
    sheet = Image.new("RGBA", (pad + cols * (size + pad), pad + len(rows) * (size + pad)), PALETTE["navy_dark"])
    draw = ImageDraw.Draw(sheet)
    for r, row in enumerate(rows):
        for c, img in enumerate(row):
            x, y = pad + c * (size + pad), pad + r * (size + pad)
            draw.rectangle([x, y, x + size - 1, y + size - 1], fill=PALETTE["sand"])
            big = img.resize((size, size), Image.NEAREST)
            sheet.alpha_composite(big, (x, y))
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
