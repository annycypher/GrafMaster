"""Каталог брендов из шаблонов SVG.

Имя бренда берётся из имени файла шаблона: «GEOS_AL-KO.svg» → «GEOS».
Универсальный вариант — «Стандарт» (файл Standard.svg).
"""
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parents[3] / "assets" / "templates"
STANDARD = "Стандарт"
_EXCLUDE = ("стикер", "stiker", "sticker", "standard", "стандарт")


def brand_from_filename(stem: str) -> str:
    for sep in ("_", " ", "-", "."):
        if sep in stem:
            return stem.split(sep)[0]
    return stem


def discover_brands() -> list[str]:
    """Список брендов: «Стандарт» + бренды из имён SVG-шаблонов."""
    brands: list[str] = [STANDARD]
    for path in sorted(TEMPLATES_DIR.glob("*.svg")):
        low = path.stem.lower()
        if any(x in low for x in _EXCLUDE):
            continue
        brand = brand_from_filename(path.stem)
        if brand and brand not in brands:
            brands.append(brand)
    return brands


def template_for_brand(brand: str) -> Path | None:
    """Путь к SVG-шаблону для бренда (или универсального «Стандарт»)."""
    if brand == STANDARD:
        path = TEMPLATES_DIR / "Standard.svg"
        return path if path.exists() else None
    for path in sorted(TEMPLATES_DIR.glob(f"{brand}*.svg")):
        if brand_from_filename(path.stem).lower() == brand.lower():
            return path
    return None
