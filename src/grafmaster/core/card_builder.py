"""Сборка карточек 900×1200 из товара (Этап 4).

Набор из 7 карточек: плашка с названием (Russo One) + фото товара +
1–2 характеристики на карточку. Всё рендерится через Pillow + наши шрифты.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from grafmaster.core import fonts as fontlib

W, H = 900, 1200
PLATE_DEFAULT = "#A855F7"
DARK = "#150B20"

# Сколько характеристик на каждую из 7 карточек (в сумме до 10)
LAYOUT = [1, 2, 1, 2, 1, 2, 1]
# Служебные/неинформативные характеристики — пропускаем
SKIP = {"Артикул", "Длина", "Ширина", "Высота", "Вес", "Вес, кг"}


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(fontlib.ASSETS_FONTS / name), size)


def pick_chars(chars: list[tuple[str, str]], limit: int = 10) -> list[tuple[str, str]]:
    """Выбирает информативные характеристики (1–2 на карточку).

    Пропускает: служебные (Артикул и габариты) и плейсхолдеры (#PROP_...),
    пустые значения.
    """
    picked: list[tuple[str, str]] = []
    for title, value in chars:
        title = (title or "").strip()
        value = (value or "").strip()
        if not title or not value:
            continue
        if title in SKIP or "#" in title or "#" in value:
            continue
        picked.append((title, value))
    return picked[:limit]


def _load_photo(path: Path | str, max_w: int = 720, max_h: int = 460) -> Image.Image:
    img = Image.open(path)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, img).convert("RGB")
    else:
        img = img.convert("RGB")
    img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    return img


def build_card(name: str, chars: list[tuple[str, str]],
               photo_path: Path | None, index: int, total: int = 7,
               plate: str = PLATE_DEFAULT, out_dir: Path | str | None = None) -> Path:
    img = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(img)

    # Верхняя плашка
    d.rectangle([0, 0, W, 200], fill=plate)
    d.text((48, 44), name, font=_font("RussoOne-Regular.ttf", 44), fill="#FFFFFF")
    d.text((50, 122), f"Карточка {index} из {total}",
           font=_font("Rubik-Regular.ttf", 26), fill="#FFFFFF")

    # Зона фото товара
    d.rounded_rectangle([60, 240, 840, 780], radius=24, fill="#F4F6F8",
                        outline="#C9D2DC", width=4)
    if photo_path and Path(photo_path).exists():
        photo = _load_photo(photo_path)
        pw, ph = photo.size
        px = 60 + (780 - pw) // 2
        py = 240 + (540 - ph) // 2
        img.paste(photo, (px, py))
    else:
        d.text((450, 510), "ФОТО ТОВАРА",
               font=_font("RussoOne-Regular.ttf", 40), fill="#A9B4C0", anchor="mm")

    # Характеристики (1–2)
    y = 820
    for i, (label, value) in enumerate(chars[:2], start=1):
        d.rounded_rectangle([60, y, 840, y + 124], radius=18, fill="#F6F7F9",
                            outline="#D5DBE1")
        d.rounded_rectangle([86, y + 36, 132, y + 88], radius=12, fill=plate)
        d.text((109, y + 62), str(i), font=_font("RussoOne-Regular.ttf", 30),
               fill="#FFFFFF", anchor="mm")
        d.text((162, y + 38), label, font=_font("Rubik-Regular.ttf", 28), fill="#5B6472")
        d.text((162, y + 76), value, font=_font("RussoOne-Regular.ttf", 32), fill="#111827")
        y += 140

    # Нижняя плашка
    d.rectangle([0, H - 80, W, H], fill=DARK)
    d.text((W // 2, H - 40), "GrafMaster · 900×1200",
           font=_font("Rubik-Regular.ttf", 24), fill="#C084FC", anchor="mm")

    if out_dir is None:
        raise ValueError("out_dir обязателен")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    file = out / f"{index:03d}.png"
    img.save(file)
    return file


def build_set(name: str, chars: list[tuple[str, str]], photo_path: Path | None,
              out_dir: Path | str, plate: str = PLATE_DEFAULT) -> list[Path]:
    """7 карточек одного товара: имя_001.png … имя_007.png."""
    files: list[Path] = []
    idx = 0
    for card_no, slots in enumerate(LAYOUT, start=1):
        card_chars = chars[idx:idx + slots]
        idx += slots
        files.append(build_card(name, card_chars, photo_path, card_no, 7, plate, out_dir))
    return files
