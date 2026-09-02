"""Парсер SVG-шаблона карточки: слои, z-порядок, зона фото, название, иконки.

Понимает структуру из макета:
  нижний слой — изображение (фон/фото на белом),
  средние — иконки и характеристики,
  верхний — векторная графика и крупное название.
Порядок в документе SVG = порядок наложения (снизу вверх).
"""
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

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


@dataclass
class SvgTemplate:
    width: float = 900.0
    height: float = 1200.0
    layers: list[TemplateLayer] = field(default_factory=list)
    name: str = ""
    photo: TemplateLayer | None = None


def _num(value: str | None, default: float = 0.0) -> float:
    if not value:
        return default
    m = re.match(r"[-+]?[0-9]*\.?[0-9]+", value.strip())
    return float(m.group(0)) if m else default


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _fill_of(el) -> str:
    fill = el.get("fill")
    if fill:
        return fill if fill != "none" else "#000000"
    style = el.get("style", "")
    m = re.search(r"fill:\s*([^;]+)", style)
    return m.group(1).strip() if m else "#000000"


def _classify(tag: str, x: float, y: float, w: float, h: float,
              text: str, fs: float, W: float, H: float) -> str:
    if tag == "image":
        return "photo"
    if tag == "text":
        if any(ch in text for ch in ICON_HINTS):
            return "icon"
        return "title" if fs >= 40 and y <= H * 0.25 else "text"
    if tag == "rect" and w >= W * 0.95 and h >= H * 0.95:
        return "bg"
    return "vector"


def parse_svg(path: str | Path) -> SvgTemplate:
    tree = ET.parse(path)
    root = tree.getroot()
    width = _num(root.get("width"), 900.0)
    height = _num(root.get("height"), 1200.0)
    layers: list[TemplateLayer] = []
    z = 0
    for el in root.iter():
        tag = _local(el.tag)
        if tag in ("defs", "title", "desc", "metadata", "style"):
            continue
        x = _num(el.get("x"))
        y = _num(el.get("y"))
        w = _num(el.get("width"))
        h = _num(el.get("height"))
        text = ""
        fs = 0.0
        if tag == "text":
            text = " ".join("".join(el.itertext()).split())
            fs = _num(el.get("font-size"), 14.0)
            w = max(w, len(text) * fs * 0.6)
            h = max(h, fs * 1.25)
        kind = _classify(tag, x, y, w, h, text, fs, width, height)
        layers.append(TemplateLayer(
            kind=kind, x=x, y=y, w=w, h=h, text=text, font_size=fs,
            fill=_fill_of(el), opacity=_num(el.get("opacity"), 1.0), z=z))
        z += 1

    tmpl = SvgTemplate(width=width, height=height, layers=layers)
    for layer in layers:
        if layer.kind == "title" and not tmpl.name:
            tmpl.name = layer.text
        if layer.kind == "photo" and tmpl.photo is None:
            tmpl.photo = layer
    return tmpl
