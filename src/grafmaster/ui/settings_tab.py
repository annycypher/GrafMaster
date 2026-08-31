"""Вкладка «Настройки»: ключ DeepSeek, движки, палитра, формат."""
from PySide6.QtWidgets import (
    QColorDialog, QComboBox, QFormLayout, QLineEdit, QPushButton, QVBoxLayout,
    QWidget,
)

from grafmaster.ui.widgets import make_ghost


class SettingsTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)

        form = QFormLayout()

        self.inp_key = QLineEdit()
        self.inp_key.setPlaceholderText("sk-...")
        self.inp_key.setEchoMode(QLineEdit.Password)
        form.addRow("DeepSeek API-ключ (хранится локально)", self.inp_key)

        self.combo_build = QComboBox()
        self.combo_build.addItems(["Pillow", "Inkscape", "PS/Corel"])
        form.addRow("Движок сборки", self.combo_build)

        self.combo_bg = QComboBox()
        self.combo_bg.addItems(["rembg", "SAM2 (GPU)"])
        form.addRow("Замена фона", self.combo_bg)

        self.btn_icon_folder = make_ghost(QPushButton("📂 Выбрать папку иконок"))
        form.addRow("Ваши иконки (PNG/SVG)", self.btn_icon_folder)

        self.btn_color = QPushButton("Основной цвет")
        self.btn_color.clicked.connect(self._pick_color)
        form.addRow("Палитра", self.btn_color)

        self.inp_size = QLineEdit("900 × 1200 px")
        form.addRow("Размер", self.inp_size)

        self.combo_font = QComboBox()
        self.combo_font.addItems(["Inter", "Manrope", "Rubik"])
        form.addRow("Шрифт", self.combo_font)

        root.addLayout(form)
        root.addStretch(1)

    def _pick_color(self) -> None:
        color = QColorDialog.getColor()
        if color.isValid():
            self.btn_color.setStyleSheet(f"background: {color.name()}; color: #fff;")
