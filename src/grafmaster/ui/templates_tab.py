"""Вкладка «Шаблоны»: конструктор «по образцу» (Этап 9)."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QSplitter,
    QVBoxLayout, QWidget,
)

from grafmaster.ui.widgets import make_ghost


class TemplatesTab(QWidget):
    """Загрузка образца -> авто-зоны -> сохранение шаблона."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)

        bar = QHBoxLayout()
        bar.addWidget(QPushButton("Загрузить образец"))
        inp = QLineEdit()
        inp.setPlaceholderText("или найти образец в интернете...")
        bar.addWidget(inp)
        bar.addWidget(make_ghost(QPushButton("Найти")))
        bar.addStretch(1)
        root.addLayout(bar)

        split = QSplitter(Qt.Horizontal)

        zones = QWidget()
        zv = QVBoxLayout(zones)
        zv.setContentsMargins(0, 0, 0, 0)
        for text in ("Зона фото товара (авто)", "Плашка названия",
                     "Текстовый блок из Excel", "Иконки"):
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(
                "border: 1px dashed #a855f7; border-radius: 10px;"
                "padding: 24px; color: #a58fc9;")
            zv.addWidget(lbl)
        split.addWidget(zones)

        right = QListWidget()
        right.addItem("Фото (90×120px) ✓")
        right.addItem("Плашка (низ) ✓")
        right.addItem("Тексты ×2 ✓")
        split.addWidget(right)

        split.setSizes([700, 300])
        root.addWidget(split, 1)

        bar2 = QHBoxLayout()
        bar2.addStretch(1)
        bar2.addWidget(QPushButton("Сохранить шаблон"))
        root.addLayout(bar2)
