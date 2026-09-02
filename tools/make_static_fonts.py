"""Создаёт статические TTF из вариативных (для Qt и Pillow)."""
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

DST = Path(r"C:/Users/Anna/.cline/data/workspaces/chat/GrafMaster/assets/fonts")

JOBS = [
    ("Rubik.ttf", [
        ("Rubik-Regular.ttf", {"wght": 400}),
        ("Rubik-Medium.ttf", {"wght": 500}),
        ("Rubik-Bold.ttf", {"wght": 700}),
    ]),
    ("Manrope.ttf", [
        ("Manrope-Regular.ttf", {"wght": 400}),
        ("Manrope-Bold.ttf", {"wght": 700}),
    ]),
    ("Inter.ttf", [
        ("Inter-Regular.ttf", {"wght": 400, "opsz": 14}),
        ("Inter-Medium.ttf", {"wght": 500, "opsz": 14}),
        ("Inter-Bold.ttf", {"wght": 700, "opsz": 14}),
    ]),
]

for src_name, outputs in JOBS:
    src = DST / src_name
    if not src.exists():
        print("SKIP (no source):", src_name)
        continue
    for out_name, axes in outputs:
        out = DST / out_name
        print("Instancing", src_name, "->", out_name, axes)
        font = TTFont(str(src))
        instance = instantiateVariableFont(font, axes, inplace=False)
        instance.save(str(out))
        print("  OK size:", out.stat().st_size)
