"""Каталог шрифтов GrafMaster — 20+ свободных шрифтов с кириллицей.

Все лицензии свободные (OFL / Apache 2.0) — как шрифты в Figma.
Файлы генерируются скриптом tools/download_fonts.py в assets/fonts.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class FontEntry:
    name: str
    file: str        # файл в assets/fonts
    license: str     # OFL / Apache / SIL


CATALOG: list[FontEntry] = [
    FontEntry("Russo One", "RussoOne-Regular.ttf", "OFL"),
    FontEntry("Montserrat", "Montserrat-Regular.ttf", "OFL"),
    FontEntry("Open Sans", "OpenSans-Regular.ttf", "Apache"),
    FontEntry("Roboto", "Roboto-Regular.ttf", "Apache"),
    FontEntry("Roboto Condensed", "RobotoCondensed-Regular.ttf", "Apache"),
    FontEntry("Oswald", "Oswald-Regular.ttf", "OFL"),
    FontEntry("Play", "Play-Regular.ttf", "OFL"),
    FontEntry("Exo 2", "Exo2-Regular.ttf", "OFL"),
    FontEntry("PT Sans", "PTSans-Regular.ttf", "OFL"),
    FontEntry("Lora", "Lora-Regular.ttf", "OFL"),
    FontEntry("Merriweather", "Merriweather-Regular.ttf", "OFL"),
    FontEntry("Playfair Display", "PlayfairDisplay-Regular.ttf", "OFL"),
    FontEntry("Comfortaa", "Comfortaa-Regular.ttf", "OFL"),
    FontEntry("Jura", "Jura-Regular.ttf", "OFL"),
    FontEntry("Cuprum", "Cuprum-Regular.ttf", "OFL"),
    FontEntry("Forum", "Forum-Regular.ttf", "OFL"),
    FontEntry("Caveat", "Caveat-Regular.ttf", "OFL"),
    FontEntry("Lobster", "Lobster-Regular.ttf", "OFL"),
    FontEntry("PT Serif", "PTSerif-Regular.ttf", "OFL"),
    FontEntry("Raleway", "Raleway-Regular.ttf", "OFL"),
    FontEntry("Rubik", "Rubik-Regular.ttf", "OFL"),
    FontEntry("Manrope", "Manrope-Regular.ttf", "OFL"),
]


def family_names() -> list[str]:
    return [e.name for e in CATALOG]
