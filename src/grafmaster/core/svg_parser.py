"""Парсер SVG-шаблона карточки: слои, z-порядок, зона фото, название, иконки.

Поддерживает экспорт CorelDRAW: цвета и шрифты через CSS-классы (.filN, .fntN),
встроенные изображения через xlink:href. Порядок в документе = z-порядок.
"""
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

XLINK = "{http://www.w3.org/1999/xlink}href"
ICON_HINTS = ("⚡", "🔋", "🛠", "⭐", "✅", "🔥", "💧", "🧰", "🔒", "📦", "❤️", "❄️")


@dataclass
class TemplateLayer:
    kind: str            # bg | title | photo | text | icon | vector
    x: float = 0.0
    y: float = 0.0
    w: float = 0.0
    h: float = 0.0
    text: str = ""
    font_size: float = 0.0
    fill: str = "#000000"
    opacity: float = 1.0
    z: int = 0
    href: str = ""       # для photo/icon-изображений


@dataclass
class SvgTemplate:
    width: float = 900.0
    height: float = 1200.0
    layers: list[TemplateLayer] = field(default_factory=list)
    name: str = ""
    photo: TemplateLayer | None = None
    path: str = ""


def _num(value: str | None, default: float = 0.0) -> float:
    if not value:
        return default
    m = re.match(r"[-+]?[0-9]*\.?[0-9]+", value.strip())
    return float(m.group(0)) if m else default


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _parse_css(style_text: str) -> tuple[dict, dict]:
    """Из <style> достаёт .cls {fill:..} и .cls {font-size:..}."""
    fills: dict[str, str] = {}
    fonts: dict[str, float] = {}
    for m in re.finditer(r"\.([A-Za-z0-9_\-]+)\s*\{([^}]*)\}", style_text):
        cls, body = m.group(1), m.group(2)
        fill = re.search(r"fill\s*:\s*([^;]+)", body)
        fs = re.search(r"font-size\s*:\s*([\d.]+)", body)
        if fill:
            fills[cls] = fill.group(1).strip()
        if fs:
            fonts[cls] = float(fs.group(1))
    return fills, fonts


def _classes(el) -> list[str]:
    return (el.get("class") or "").split()


def _fill_of(el, fills: dict) -> str:
    for cls in _classes(el):
        if cls in fills:
            return fills[cls]
    fill = el.get("fill")
    if fill:
        return fill if fill != "none" else "#000000"
    m = re.search(r"fill\s*:\s*([^;]+)", el.get("style", ""))
    return m.group(1).strip() if m else "#000000"


def _font_size(el, fonts: dict) -> float:
    for cls in _classes(el):
        if cls in fonts:
            return fonts[cls]
    m = re.search(r"font-size\s*:\s*([\d.]+)", el.get("style", ""))
    if m:
        return float(m.group(1))
    return _num(el.get("font-size"), 0.0)


def _classify(tag: str, y: float, w: float, h: float, W: float, H: float) -> str:
    if tag == "image":
        # Полноразмерное изображение = фото товара на белом фоне;
        # остальные картинки = иконки характеристик.
        if w >= W * 0.85 and h >= H * 0.85:
            return "photo"
        return "icon"
    if tag == "text":
        return "text"
    if tag == "rect" and w >= W * 0.95 and h >= H * 0.95:
        return "bg"
    return "vector"


def parse_svg(path: str | Path) -> SvgTemplate:
    tree = ET.parse(path)
    root = tree.getroot()
    width = _num(root.get("width"), 900.0)
    height = _num(root.get("height"), 1200.0)

    fills: dict[str, str] = {}
    fonts: dict[str, float] = {}
    for style_el in root.iter():
        if _local(style_el.tag) == "style" and style_el.text:
            f1, f2 = _parse_css(style_el.text)
            fills.update(f1)
            fonts.update(f2)

    layers: list[TemplateLayer] = []
    z = 0
    for el in root.iter():
        tag = _local(el.tag)
        if tag in ("defs", "title", "desc", "metadata", "style", "font", "glyph",
                   "font-face", "font-face-src", "font-face-name", "missing-glyph"):
            continue
        x = _num(el.get("x"))
        y = _num(el.get("y"))
        w = _num(el.get("width"))
        h = _num(el.get("height"))
        text = ""
        fs = 0.0
        href = ""
        if tag == "text":
            text = " ".join("".join(el.itertext()).split())
            fs = _font_size(el, fonts)
            w = max(w, len(text) * max(fs, 12) * 0.6)
            h = max(h, max(fs, 12) * 1.25)
        if tag == "image":
            href = el.get(XLINK) or el.get("href") or ""
        kind = _classify(tag, y, w, h, width, height)
        layers.append(TemplateLayer(
            kind=kind, x=x, y=y, w=w, h=h, text=text, font_size=fs,
            fill=_fill_of(el, fills), opacity=_num(el.get("opacity"), 1.0),
            z=z, href=href))
        z += 1

    tmpl = SvgTemplate(width=width, height=height, layers=layers, path=str(path))

    # Название: самый крупный текст в верхней трети карточки
    texts = [l for l in layers if l.kind == "text" and l.y <= height * 0.35 and l.text]
    if texts:
        tmpl.name = max(texts, key=lambda l: l.font_size).text

    # Главное фото: полноразмерное изображение (товар на белом фоне)
    photos = [l for l in layers if l.kind == "photo"]
    tmpl.photo = max(photos, key=lambda l: l.w * l.h) if photos else None
    return tmpl

