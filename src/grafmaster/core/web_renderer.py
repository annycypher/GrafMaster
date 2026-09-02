"""Сборка карточки для веб-версии: подстановка данных в SVG-шаблон.

SVG рендерится в браузере. Здесь:
- название становится тёмно-серым с градиентом;
- характеристики и подпись модели рисуются шрифтом Russo One (Google Fonts);
- авто-подгонка размера шрифта, чтобы текст не выходил за границы слоя.
"""
import base64
import re
from pathlib import Path

STICKER_HINTS = ("ОСТЕРЕГАЙТЕСЬ", "ПОДДЕЛОК", "остерегайтесь", "подделок")
RUSSO = ("<style>@import url('https://fonts.googleapis.com/css2?"
         "family=Russo+One&display=swap');</style>")
GRADIENT = ('<linearGradient id="gmTitle" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#3f3f46"/>'
            '<stop offset="1" stop-color="#a1a1aa"/></linearGradient>')


def _num_part(value: str) -> str:
    m = re.match(r"[-+]?[0-9]*\.?[0-9]+", value.strip())
    return m.group(0) if m else value.strip()


def _b64_photo(path: str) -> str:
    with open(path, "rb") as fh:
        data = base64.b64encode(fh.read()).decode("ascii")
    return "data:image/png;base64," + data


def _num_pattern(value: float) -> str:
    s = str(value)
    if s.endswith(".0"):
        return re.escape(s[:-2]) + r"(?:\.0+)?"
    return re.escape(s)


def _text_tag_at(text: str, x: float, y: float, new_content: str,
                 style: str = "") -> str:
    """Заменяет содержимое <text> по координатам x/y и добавляет inline-style."""
    xp, yp = _num_pattern(x), _num_pattern(y)
    pattern = re.compile(r"(<text\b(?=[^>]*\bx=\"" + xp + r"\")"
                         r"(?=[^>]*\by=\"" + yp + r"\")[^>]*)\s*>([^<]*)</text>")

    def _repl(m):
        head = m.group(1)
        head = re.sub(r'\s*style="[^"]*"', "", head)
        extra = f' style="{style}"' if style else ""
        return head + extra + ">" + new_content + "</text>"

    return pattern.sub(_repl, text, count=1)


def _title_of(template):
    return next((l for l in template.layers
                 if l.kind == "text" and l.text
                 and l.y < template.height * 0.3 and l.font_size >= 40), None)


def _assign_characteristics(template, characteristics):
    title = _title_of(template)
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


def _model_layer(template):
    for layer in template.layers:
        if layer.kind != "text" or not layer.text:
            continue
        if layer.y < template.height * 0.35:
            continue
        if any(h in layer.text.upper() for h in STICKER_HINTS):
            continue
        if re.search(r"[A-Za-zА-Яа-я]{2,}[\s\-]*\d", layer.text):
            return layer
    return None


def substitute_svg(template, svg_text: str, name: str,
                   characteristics: list[tuple[str, str]],
                   photo_path: str | None = None,
                   model: str = "") -> str:
    text = svg_text

    # шрифт Russo One (после открывающего <svg>) + градиент внутри <defs>
    m = re.search(r"<svg[^>]*>", text)
    if m:
        text = text[:m.end()] + RUSSO + text[m.end():]
    defs_i = text.find("<defs")
    if defs_i != -1:
        end = text.find(">", defs_i)
        text = text[:end + 1] + GRADIENT + text[end + 1:]
    else:
        m = re.search(r"<svg[^>]*>", text)
        if m:
            text = text[:m.end()] + GRADIENT + text[m.end():]

    # фото товара в зону photo (data URI)
    if photo_path and template.photo and template.photo.href:
        href = template.photo.href
        data = _b64_photo(photo_path)
        for variant in (href, href.replace("\\", "/"), href.replace("/", "\\")):
            text = text.replace(f'href="{variant}"', f'href="{data}"')
            text = text.replace(f'xlink:href="{variant}"', f'xlink:href="{data}"')

    # название: тёмно-серый градиент + Russo One
    title = _title_of(template)
    if title:
        style = "fill:url(#gmTitle);font-family:'Russo One';font-weight:400"
        text = _text_tag_at(text, title.x, title.y,
                            (name or template.name or "ТОВАР").upper(), style)

    # характеристики: метки и значения (Russo One, автоподгонка)
    label_map, value_map = _assign_characteristics(template, characteristics)
    for layer in template.layers:
        if layer.z in value_map:
            content = _num_part(value_map[layer.z]) or value_map[layer.z]
        elif layer.z in label_map:
            content = label_map[layer.z]
        else:
            continue
        if not content:
            continue
        fill = layer.fill if layer.fill.startswith("#") else "#333333"
        fs = layer.font_size
        if layer.w > 0:
            fit = int(layer.w / (len(content) * 0.6 + 0.001))
            fs = max(12, min(fs, fit))
        style = f"fill:{fill};font-family:'Russo One';font-size:{fs}px"
        text = _text_tag_at(text, layer.x, layer.y, content, style)

    # подпись модели (GEOS CSP240 → model)
    model_layer = _model_layer(template)
    if model_layer and model:
        fill = model_layer.fill if model_layer.fill.startswith("#") else "#80B5EC"
        style = f"fill:{fill};font-family:'Russo One';font-size:{int(model_layer.font_size)}px"
        text = _text_tag_at(text, model_layer.x, model_layer.y, model, style)

    return text

