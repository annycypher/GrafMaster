"""Рендер карточки по SVG-шаблону бренда.

Шаблон рендерится как есть (вся графика — из SVG), поверх подставляются:
- фото товара в зону photo;
- название вместо крупного заголовка;
- характеристики вместо текстов-значений шаблона.
"""
from pathlib import Path

from PIL import Image
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from grafmaster.core import fonts as fontlib

W, H = 900, 1200
STICKER_HINTS = ("ОСТЕРЕГАЙТЕСЬ", "ПОДДЕЛОК", "остерегайтесь", "подделок")


def _load_photo(path: str, max_w: int, max_h: int) -> Image.Image:
    img = Image.open(path)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, img).convert("RGB")
    else:
        img = img.convert("RGB")
    img.thumbnail((max(20, max_w), max(20, max_h)), Image.Resampling.LANCZOS)
    return img


def _qimage_from_pil(pil_img: Image.Image) -> QImage:
    img = pil_img.convert("RGB")
    data = img.tobytes("raw", "RGB")
    q = QImage(data, img.width, img.height, img.width * 3, QImage.Format_RGB888)
    return q.copy()


def _assign_characteristics(template, characteristics):
    """Раздаёт характеристики по текстовым слоям: цифры->значения, слова->метки."""
    region = [l for l in template.layers
              if l.kind == "text" and l.text
              and 100 < l.y < template.height * 0.55
              and not any(h in l.text.upper() for h in STICKER_HINTS)]
    region.sort(key=lambda l: (round(l.y / 8), l.x))
    values = [l for l in region if any(c.isdigit() for c in l.text)]
    labels = [l for l in region if not any(c.isdigit() for c in l.text)]
    label_map, value_map = {}, {}
    for i, (lbl, val) in enumerate(characteristics):
        if i < len(labels):
            label_map[labels[i].z] = lbl
        if i < len(values):
            value_map[values[i].z] = val
    return label_map, value_map


def render_card(template, svg_path: str, name: str,
                characteristics: list[tuple[str, str]], photo_path: str | None,
                out_path: str) -> str:
    renderer = QSvgRenderer(svg_path)
    img = QImage(W, H, QImage.Format_ARGB32)
    img.fill(Qt.white)
    p = QPainter(img)
    renderer.render(p, QRectF(0, 0, W, H))

    # --- фото товара в зону photo ---
    photo_layer = template.photo
    if photo_layer and photo_path and Path(photo_path).exists():
        try:
            pil = _load_photo(photo_path, photo_layer.w - 16, photo_layer.h - 16)
            q = _qimage_from_pil(pil)
            px = int(photo_layer.x + (photo_layer.w - q.width()) / 2)
            py = int(photo_layer.y + (photo_layer.h - q.height()) / 2)
            p.drawImage(px, py, q)
        except Exception:  # noqa: BLE001
            pass

    # --- название вместо крупного заголовка ---
    title = next((l for l in template.layers
                  if l.kind == "text" and l.text and l.y < template.height * 0.3
                  and l.font_size >= 40), None)
    if title:
        p.setFont(QFont(fontlib.preferred_family(), int(title.font_size)))
        p.setPen(QColor(title.fill if title.fill.startswith("#") else "#ffffff"))
        p.drawText(int(title.x), int(title.y),
                   (name or template.name or "ТОВАР").upper())

    # --- характеристики: метки и значения ---
    label_map, value_map = _assign_characteristics(template, characteristics)
    for layer in template.layers:
        if layer.z in label_map or layer.z in value_map:
            text = label_map.get(layer.z) or value_map.get(layer.z)
            p.setFont(QFont(fontlib.preferred_family(), int(layer.font_size)))
            p.setPen(QColor(layer.fill if layer.fill.startswith("#") else "#333333"))
            p.drawText(int(layer.x), int(layer.y), text)

    p.end()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return out_path
