"""Окно выбора шрифта с предпоказом (каталог свободных шрифтов)."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QLabel, QListWidget, QListWidgetItem,
    QVBoxLayout, QWidget,
)

from grafmaster.core.font_catalog import FontEntry
from grafmaster.core.fonts import available_entries

PREVIEW_TEXT = "Аа Бб Вв Гг Дд Её Жж 0123456789 · Инфографика 900×1200"


class FontDialog(QDialog):
    """Список шрифтов с живым предпоказом; возвращает выбранную семью."""

    def __init__(self, current: str = "Russo One",
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Выбор шрифта")
        self.setModal(True)
        self.resize(560, 520)
        self._entries: list[FontEntry] = available_entries()

        root = QVBoxLayout(self)
        root.addWidget(QLabel("Шрифты (свободные лицензии OFL/Apache, кириллица):"))

        self.list = QListWidget()
        for entry in self._entries:
            item = QListWidgetItem(f"{entry.name}  —  {PREVIEW_TEXT}")
            item.setData(Qt.UserRole, entry.name)
            f = QFont(entry.name, 13)
            item.setFont(f)
            self.list.addItem(item)
            if entry.name == current:
                self.list.setCurrentItem(item)
        self.list.currentItemChanged.connect(self._on_select)
        root.addWidget(self.list, 1)

        self.preview = QLabel(PREVIEW_TEXT)
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(96)
        self.preview.setStyleSheet(
            "border: 1px solid #513a77; border-radius: 12px;"
            "background: #1c112e; color: #f1eaff; font-size: 26px;")
        root.addWidget(self.preview)

        box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        root.addWidget(box)

        if self.list.currentItem():
            self._on_select(self.list.currentItem())

    def _on_select(self, item: QListWidgetItem | None) -> None:
        if item is None:
            return
        family = item.data(Qt.UserRole)
        self.preview.setFont(QFont(family, 26))

    def chosen_family(self) -> str | None:
        item = self.list.currentItem()
        return item.data(Qt.UserRole) if item else None

    @staticmethod
    def get_font(current: str = "Russo One",
                 parent: QWidget | None = None) -> str | None:
        dlg = FontDialog(current, parent)
        if dlg.exec() == QDialog.Accepted:
            return dlg.chosen_family()
        return None
