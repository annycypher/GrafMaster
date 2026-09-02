"""Сборка карточки для веб-версии: подстановка данных в SVG-шаблон.

SVG рендерится в браузере (клиент), поэтому серверу не нужны cairo/Qt.
Здесь — подстановка названия, характеристик и фото прямо в текст SVG.
"""
import base64
import re
from pathlib import Path

STICKER_HINTS = ("ОСТЕРЕГАЙТЕСЬ", "ПОДДЕЛОК", "остерегайтесь", "подделок")


def _b64_photo(path: str) -> str:
    with open(path, "rb") as fh:
        data = base64.b64encode(fh.read()).decode("ascii")
    return "data:image/png;base64," + data


def _replace_text_at(text: str, x: float, y: float, new_text: str) -> str:
    xp, yp = re.escape(str(x)), re.escape(str(y))
    pattern = (r"<text\b(?=[^>]*\bx=\"" + xp + r"\")"
               r"(?=[^>]*\by=\"" + yp + r"\")[^>]*>([^<]*)</text>")
    return re.sub(pattern, lambda m: m.group(0).replace(m.group(1), new_text),
                  text, count=1)


def _assign_characteristics(template, characteristics):
    title = next((l for l in template.layers
                  if l.kind == "text" and l.text
                  and l.y < template.height * 0.3 and l.font_size >= 40), None)
    title_z = title.z if title else -1
    region = [l for l in template.layers
              if l.kind == "text" and l.text and l.z != title_z
              and 100 < l.y < template.height * 0.45
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


def substitute_svg(template, svg_text: str, name: str,
                   characteristics: list[tuple[str, str]],
                   photo_path: str | None = None) -> str:
    text = svg_text

    # 1) фото товара в зону photo (data URI)
    if photo_path and template.photo and template.photo.href:
        href = template.photo.href
        data = _b64_photo(photo_path)
        for variant in (href, href.replace("\\", "/"), href.replace("/", "\\")):
            text = text.replace(f'href="{variant}"', f'href="{data}"')
            text = text.replace(f'xlink:href="{variant}"', f'xlink:href="{data}"')

    # 2) название вместо крупного заголовка
    title = next((l for l in template.layers
                  if l.kind == "text" and l.text
                  and l.y < template.height * 0.3 and l.font_size >= 40), None)
    if title:
        text = _replace_text_at(text, title.x, title.y,
                                (name or template.name or "ТОВАР").upper())

    # 3) характеристики: метки и значения
    label_map, value_map = _assign_characteristics(template, characteristics)
    for layer in template.layers:
        new_text = label_map.get(layer.z) or value_map.get(layer.z)
        if new_text and layer.text:
            text = _replace_text_at(text, layer.x, layer.y, new_text)

    return text
