"""Шрифты GrafMaster: каталог, регистрация в Qt, выбор семьи.

Основной шрифт — Russo One (кириллица). Полный каталог — 20+ свободных
шрифтов (OFL/Apache) в assets/fonts. Файлы нужны и для рендера Pillow.
"""
from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont, QFontDatabase

from grafmaster.core.font_catalog import CATALOG, FontEntry

# Корень проекта: GrafMaster/src/grafmaster/core/fonts.py -> parents[3]
ASSETS_FONTS = Path(__file__).resolve().parents[3] / "assets" / "fonts"
_SETTINGS = QSettings("GrafMaster", "GrafMaster")

DEFAULT_FAMILY = "Russo One"


def available_entries() -> list[FontEntry]:
    """Записи каталога, файлы которых реально лежат в assets/fonts."""
    return [e for e in CATALOG if (ASSETS_FONTS / e.file).exists()]


def register_fonts() -> list[str]:
    """Регистрирует все TTF из assets/fonts в Qt, возвращает семьи."""
    families: list[str] = []
    for path in sorted(ASSETS_FONTS.glob("*.ttf")):
        fid = QFontDatabase.addApplicationFont(str(path))
        if fid != -1:
            families.extend(QFontDatabase.applicationFontFamilies(fid))
    return families


def chosen_family() -> str:
    return str(_SETTINGS.value("font_family", DEFAULT_FAMILY))


def set_chosen_family(name: str) -> None:
    _SETTINGS.setValue("font_family", name)


def preferred_family(families: list[str] | None = None) -> str:
    """Приоритет: выбранный пользователем -> Russo One -> системные."""
    families = families if families is not None else register_fonts()
    system = QFontDatabase.families()
    candidates = (chosen_family(), DEFAULT_FAMILY, "Rubik", "Segoe UI", "Arial")
    for name in candidates:
        if name in families or name in system:
            return name
    return "Arial"


def default_font(size: int = 10) -> QFont:
    return QFont(preferred_family(), size)


def font_path(name: str = "RussoOne-Regular.ttf") -> Path | None:
    """Путь к файлу шрифта для Pillow (рендер карточек 900×1200)."""
    path = ASSETS_FONTS / name
    return path if path.exists() else None

