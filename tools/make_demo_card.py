"""Демо-карточка: что наш движок умеет собирать уже сейчас (900×1200, Pillow)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = Path(r"C:\Users\Anna\.cline\data\workspaces\chat\GrafMaster\assets\fonts")
OUT = Path(r"C:\Users\Anna\Desktop\Пример\demo_GrafMaster.png")


def f(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


W, H = 900, 1200
img = Image.new("RGB", (W, H), "#ffffff")
d = ImageDraw.Draw(img)

# Верхняя фиолетовая плашка с названием
d.rectangle([0, 0, W, 170], fill="#a855f7")
d.text((44, 60), "Бензопила GEOS Max CSP346", font=f("Rubik-Bold.ttf", 46), fill="#ffffff")
d.text((46, 122), "Инфографика · карточка 1 из 7", font=f("Rubik-Medium.ttf", 24), fill="#e9d5ff")

# Область фото товара
d.rounded_rectangle([60, 210, 840, 800], radius=24, fill="#ece5fa", outline="#c4b5e3", width=4)
d.text((450, 505), "ФОТО ТОВАРА", font=f("Rubik-Bold.ttf", 40), fill="#a08fc4", anchor="mm")

# Характеристики (плашки с чипами)
items = [("Мощность", "2.6 кВт"), ("Объём бака", "0.5 л"),
         ("Шина", "45 см"), ("Класс", "Профи")]
y = 850
for i, (label, value) in enumerate(items):
    d.rounded_rectangle([60, y, 840, y + 95], radius=18, fill="#f3f0fd", outline="#c4b5e3")
    d.rounded_rectangle([84, y + 22, 132, y + 70], radius=12, fill="#a855f7")
    d.text((108, y + 47), str(i + 1), font=f("Rubik-Bold.ttf", 30), fill="#ffffff", anchor="mm")
    d.text((160, y + 30), label, font=f("Rubik-Medium.ttf", 28), fill="#5b6472")
    d.text((620, y + 30), value, font=f("Rubik-Bold.ttf", 30), fill="#1f2430")
    y += 112

# Нижняя плашка
d.rectangle([0, H - 90, W, H], fill="#150b20")
d.text((W // 2, H - 45), "GrafMaster · 900×1200", font=f("Rubik-Medium.ttf", 26), fill="#c084fc", anchor="mm")

img.save(OUT)
print("SAVED:", OUT)
