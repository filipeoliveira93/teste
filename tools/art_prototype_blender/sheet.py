"""PROTOTYPE — monta a prancha das 8 direções sobre piso escuro (python comum + Pillow/numpy)."""
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).parent / "out"
DIRS = ["s", "sw", "w", "nw", "n", "ne", "e", "se"]


def floor(size):
    yy, xx = np.mgrid[0:size, 0:size] / size
    light = np.clip(1.15 - 1.4 * np.hypot(xx - 0.45, yy - 0.7), 0.3, 1.0)
    tex = 1 + np.random.default_rng(1).normal(0, 0.05, (size, size))
    rgb = np.clip(np.array([62, 56, 60]) * (light * tex)[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([rgb, np.full((size, size), 255, np.uint8)]), "RGBA")


def sheet(name, size, cols):
    pad = 6
    rows = (len(DIRS) + cols - 1) // cols
    img = Image.new("RGBA", (pad + cols * (size + pad), pad + rows * (size + pad)), (11, 10, 14, 255))
    for i, d in enumerate(DIRS):
        tile = floor(size)
        tile.alpha_composite(Image.open(OUT / f"{name}_{d}_{size}.png").convert("RGBA"))
        img.alpha_composite(tile, (pad + i % cols * (size + pad), pad + i // cols * (size + pad)))
    img.save(OUT / f"preview_{name}_{size}.png")


if __name__ == "__main__":
    sheet("knight", 128, 8)
    sheet("knight", 512, 4)
