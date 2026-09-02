"""Правая панель данных карточки: миниатюры и правка данных.

Показывает всё, что используется в карточке:
- название (правка);
- характеристики (таблица, двойной клик — правка);
- изображение (миниатюра + замена);
- шаблон (миниатюра + замена).
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from grafmaster.ui.editor_window import render_template_to_image


class CardDataPanel(QWidget):
    data_changed = Signal()

    def __init__(self, template=None, svg_path: str = "",
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.template = template
        self.svg_path = svg_path
        self.photo_path = ""
        self.setMinimumWidth(280)

        root = QVBoxLayout(self)
        root.addWidget(QLabel("НАЗВАНИЕ"))
        self.inp_title = QLineEdit()
        self.inp_title.setPlaceholderText("Название товара…")
        self.inp_title.editingFinished.connect(self.data_changed.emit)
        root.addWidget(self.inp_title)

        root.addWidget(QLabel("ХАРАКТЕРИСТИКИ (двойной клик — правка)"))
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Характеристика", "Значение"])
        self.table.setColumnWidth(0, 140)
        self.table.setColumnWidth(1, 120)
        self.table.itemChanged.connect(self._changed)
        root.addWidget(self.table, 1)

        root.addWidget(QLabel("ИЗОБРАЖЕНИЕ"))
        self.photo_lbl = QLabel("—")
        self.photo_lbl.setFixedHeight(90)
        self.photo_lbl.setAlignment(Qt.AlignCenter)
        root.addWidget(self.photo_lbl)
        self.btn_photo = QPushButton("Заменить фото…")
        self.btn_photo.clicked.connect(self._pick_photo)
        root.addWidget(self.btn_photo)

        root.addWidget(QLabel("ШАБЛОН"))
        self.tmpl_lbl = QLabel("—")
        self.tmpl_lbl.setFixedHeight(110)
        self.tmpl_lbl.setAlignment(Qt.AlignCenter)
        root.addWidget(self.tmpl_lbl)
        self.btn_tmpl = QPushButton("Заменить шаблон…")
        self.btn_tmpl.clicked.connect(self._pick_template)
        root.addWidget(self.btn_tmpl)

        self.set_template(template, svg_path)

    # ---------- данные ----------

    def set_template(self, template, svg_path: str) -> None:
        self.template = template
        self.svg_path = svg_path
        if template:
            self.inp_title.setText(template.name)
            try:
                thumb = render_template_to_image(template, svg_path, 180, 240)
                self.tmpl_lbl.setPixmap(
                    QPixmap.fromImage(thumb).scaled(
                        170, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except Exception:  # noqa: BLE001
                self.tmpl_lbl.setText("шаблон")
        else:
            self.tmpl_lbl.setText("—")

    def set_photo(self, path: str) -> None:
        self.photo_path = path
        if path:
            pix = QPixmap(path)
            self.photo_lbl.setPixmap(
                pix.scaled(200, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.photo_lbl.setText("—")

    def set_characteristics(self, items: list[tuple[str, str]]) -> None:
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for label, value in items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(label))
            self.table.setItem(row, 1, QTableWidgetItem(value))
        self.table.blockSignals(False)

    def characteristics(self) -> list[tuple[str, str]]:
        rows = []
        for r in range(self.table.rowCount()):
            lbl = self.table.item(r, 0)
            val = self.table.item(r, 1)
            if lbl and lbl.text().strip():
                rows.append((lbl.text().strip(),
                             val.text().strip() if val else ""))
        return rows

    def title(self) -> str:
        return self.inp_title.text().strip()

    def _changed(self, *_args) -> None:
        self.data_changed.emit()

    # ---------- замена ----------

    def _pick_photo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите фото товара", "", "Изображения (*.png *.jpg *.jpeg *.webp)")
        if path:
            self.set_photo(path)
            self.data_changed.emit()

    def _pick_template(self) -> None:
        from grafmaster.core import brand_catalog
        from grafmaster.ui.brand_selector import BrandSelector
        brand = BrandSelector.get_brand(self)
        if not brand:
            return
        path = brand_catalog.template_for_brand(brand)
        if path:
            from grafmaster.core import svg_parser
            self.set_template(svg_parser.parse_svg(str(path)), str(path))
            self.data_changed.emit()
