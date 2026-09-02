"""Демо-карточки в стиле ваших примеров (плашка + фото + характеристики).
Главный шрифт — Russo One. Сохраняет в Desktop/Пример для сравнения."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = Path(r"C:\Users\Anna\.cline\data\workspaces\chat\GrafMaster\assets\fonts")
OUT = Path(r"C:\Users\Anna\Desktop\Пример")


def f(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


CARDS = [
    {
        "file": "GrafMaster_Бензопила.png",
        "plate": "#E10C13",
        "name": "Бензопила GEOS Max CSP346",
        "sub": "Садово-огородная техника",
        "items": [("Мощность", "2.6 кВт"), ("Объём бака", "0.5 л"),
                  ("Шина", "45 см"), ("Вес", "4.2 кг")],
    },
    {
        "file": "GrafMaster_Перфоратор.png",
        "plate": "#008397",
        "name": "Перфоратор MAKITA HR2653",
        "sub": "Инструмент для профессионалов",
        "items": [("Мощность", "780 Вт"), ("Энергия удара", "2.8 Дж"),
                  ("Патрон", "SDS-Plus"), ("Режимы", "3")],
    },
]

W, H = 900, 1200


def build(card: dict) -> None:
    img = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(img)

    # Верхняя цветная плашка
    d.rectangle([0, 0, W, 240], fill=card["plate"])
    d.text((48, 70), card["name"], font=f("RussoOne-Regular.ttf", 52), fill="#FFFFFF")
    d.text((50, 150), card["sub"], font=f("Rubik-Regular.ttf", 28), fill="#FFFFFF")

    # Зона фото товара
    d.rounded_rectangle([60, 290, 840, 820], radius=24, fill="#F4F6F8",
                        outline="#C9D2DC", width=4)
    d.text((450, 555), "ФОТО ТОВАРА", font=f("RussoOne-Regular.ttf", 40),
           fill="#A9B4C0", anchor="mm")

    # Характеристики
    y = 860
    for i, (label, value) in enumerate(card["items"]):
        d.rounded_rectangle([60, y, 840, y + 92], radius=18, fill="#F6F7F9",
                            outline="#D5DBE1")
        d.rounded_rectangle([86, y + 24, 132, y + 68], radius=12, fill=card["plate"])
        d.text((109, y + 46), str(i + 1), font=f("RussoOne-Regular.ttf", 28),
               fill="#FFFFFF", anchor="mm")
        d.text((162, y + 28), label, font=f("Rubik-Regular.ttf", 28), fill="#5B6472")
        d.text((620, y + 28), value, font=f("RussoOne-Regular.ttf", 28), fill="#111827")
        y += 108

    # Нижняя плашка
    d.rectangle([0, H - 80, W, H], fill="#150B20")
    d.text((W // 2, H - 40), "GrafMaster · 900×1200",
           font=f("Rubik-Regular.ttf", 24), fill="#C084FC", anchor="mm")

    out = OUT / card["file"]
    img.save(out)
    print("SAVED:", out)


for card in CARDS:
    build(card)
print("DONE")
