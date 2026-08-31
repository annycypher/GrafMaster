"""Чтение товаров и характеристик из Excel (.xlsx) — Этап 2.

Библиотека: openpyxl. Сейчас — каркас модели данных.
"""
from dataclasses import dataclass, field


@dataclass
class Product:
    name: str
    photo_file: str = ""
    characteristics: dict = field(default_factory=dict)


def read_products(path: str) -> list[Product]:
    """Возвращает список товаров из Excel-файла.

    Этап 2 плана:
      - openpyxl.load_workbook(path)
      - сопоставление колонок: название / фото / характеристики
      - обработка пустых ячеек, листов, кодировок
    """
    raise NotImplementedError("Этап 2 — реализация чтения Excel")
