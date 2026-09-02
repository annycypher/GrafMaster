"""Инспекция SVG CorelDRAW: font-size, классы заливки, image-теги."""
import re
from pathlib import Path

p = Path(r"C:\Users\Anna\.cline\data\workspaces\chat\GrafMaster\assets\templates\GEOS_AL-KO.svg")
text = p.read_text(encoding="utf-8")
print("len:", len(text))

fs = re.findall(r'font-size[="\s:]+([\d.]+)', text)
print("font-size values (first 30):", fs[:30], "| count:", len(fs))

m = re.search(r"<text[^>]*>[^<]*БЕНЗОПИЛА[^<]*</text>", text)
print("TEXT TAG sample:", m.group(0)[:500] if m else "not found")

imgs = re.findall(r"<image[^>]*>", text)
print("IMG count:", len(imgs))
for im in imgs[:5]:
    print("  IMG:", im[:260])

# Пример текста с Мощностью
m2 = re.search(r"<text[^>]*>[^<]*Мощность[^<]*</text>", text)
print("MOZNOST TEXT:", m2.group(0)[:500] if m2 else "not found")
