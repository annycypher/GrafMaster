"""Вкладка «Проект карточек»: редактор слоёв, Сохранить/Отмена (Этап 5)."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton,
    QSplitter, QVBoxLayout, QWidget,
)

from grafmaster.ui.widgets import CardView, make_ghost


class ProjectTab(QWidget):
    """Мини-Figma: список комплектов, карточка, слои, Сохранить/Отмена."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("Проект:"))
        bar.addWidget(QLabel("Стиральная машина"))
        bar.addStretch(1)
        for txt in ("Скачать JPG", "Скачать PDF", "Скачать SVG", "Скачать .fig"):
            bar.addWidget(make_ghost(QPushButton(txt)))
        self.btn_save = QPushButton("Сохранить")
        self.btn_cancel = make_ghost(QPushButton("Отмена"))
        bar.addWidget(self.btn_save)
        bar.addWidget(self.btn_cancel)
        root.addLayout(bar)

        split = QSplitter(Qt.Horizontal)

        left = QListWidget()
        for name in ("Стиральная машина", "Холодильник", "Микроволновка"):
            left.addItem(QListWidgetItem(name))
        split.addWidget(left)

        card_host = QWidget()
        cv = QVBoxLayout(card_host)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.addStretch(1)
        self.card = CardView()
        self.card.set_content("Стиральная машина", "Загрузка: 7 кг", "⚡")
        cv.addWidget(self.card, 0, Qt.AlignHCenter)
        cv.addStretch(1)
        split.addWidget(card_host)

        right = QListWidget()
        right.addItem("🖼 Фото товара")
        right.addItem("▮ Плашка названия")
        right.addItem("T Текст: Мощность")
        right.addItem("⚡ Иконка")
        split.addWidget(right)

        split.setSizes([220, 640, 260])
        root.addWidget(split, 1)

        self.btn_save.clicked.connect(lambda: self._flash("Проект сохранён (.gmproj)"))
        self.btn_cancel.clicked.connect(lambda: self._flash("Изменения отменены"))

    def _flash(self, msg: str) -> None:
        self.card.set_content("Стиральная машина", msg, "✅")
