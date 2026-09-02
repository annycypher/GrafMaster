"""Анализ примеров карточек: размер, палитра, профиль яркости по строкам."""
from pathlib import Path

from PIL import Image

EX = Path(r"C:\Users\Anna\Desktop\Пример")


def top_colors(img: Image.Image, n: int = 8) -> list[tuple[int, str]]:
    q = img.convert("RGB").quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette() or []
    counts = sorted(q.getcolors(), reverse=True)
    out = []
    for cnt, idx in counts[:n]:
        r, g, b = pal[idx * 3: idx * 3 + 3]
        out.append((cnt, f"#{r:02X}{g:02X}{b:02X}"))
    return out


def row_profile(img: Image.Image, segments: int = 20) -> list[float]:
    small = img.convert("RGB").resize((img.width // 6, img.height // 6))
    w, h = small.size
    px = small.load()
    rows = [sum((px[x, y][0] + px[x, y][1] + px[x, y][2]) / 3 for x in range(w)) / w
            for y in range(h)]
    seg = max(1, h // segments)
    return [round(sum(rows[i * seg:(i + 1) * seg]) / seg, 1) for i in range(segments)]


for p in sorted(EX.glob("*.jpg")):
    img = Image.open(p)
    print("FILE:", p.name, "| size:", img.size, img.mode)
    print("  top colors:", top_colors(img))
    print("  brightness by rows (top->bottom):", row_profile(img))
