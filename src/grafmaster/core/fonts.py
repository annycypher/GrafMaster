"""Работа со шрифтами: регистрация в Qt и поиск файлов для Pillow.

Шрифты лежат в assets/fonts (лицензия OFL): Inter, Rubik, Manrope.
Все поддерживают кириллицу. Регистрация в Qt гарантирует одинаковый вид
интерфейса на любом Windows, а файлы нужны для рендера карточек Pillow.
"""
from pathlib import Path

from PySide6.QtGui import QFont, QFontDatabase

# Корень проекта: GrafMaster/src/grafmaster/core/fonts.py -> parents[3] = GrafMaster
ASSETS_FONTS = Path(__file__).resolve().parents[3] / "assets" / "fonts"

# Файлы в assets/fonts (порядок = приоритет). Статические TTF с кириллицей.
_FILES = [
    "Inter-Regular.ttf", "Inter-Medium.ttf", "Inter-Bold.ttf",
    "Rubik-Regular.ttf", "Rubik-Medium.ttf", "Rubik-Bold.ttf",
    "Manrope-Regular.ttf", "Manrope-Bold.ttf",
]
_PREFERRED = ("Inter", "Rubik", "Manrope", "Segoe UI", "Arial")


def register_fonts() -> list[str]:
    """Регистрирует шрифты из assets/fonts в Qt и возвращает их семьи."""
    families: list[str] = []
    for fname in _FILES:
        path = ASSETS_FONTS / fname
        if not path.exists():
            continue
        fam_id = QFontDatabase.addApplicationFont(str(path))
        if fam_id != -1:
            families.extend(QFontDatabase.applicationFontFamilies(fam_id))
    return families


def preferred_family(families: list[str] | None = None) -> str:
    """Первая доступная семья из предпочтений (все поддерживают кириллицу)."""
    families = families if families is not None else register_fonts()
    system = QFontDatabase.families()
    for name in _PREFERRED:
        if name in families or name in system:
            return name
    return "Arial"


def default_font(size: int = 10) -> QFont:
    """QFont по умолчанию с предпочтительной семьёй."""
    return QFont(preferred_family(), size)


def font_path(name: str = "Inter-Regular.ttf") -> Path | None:
    """Путь к файлу шрифта для Pillow (рендер карточек 900×1200)."""
    path = ASSETS_FONTS / name
    return path if path.exists() else None
