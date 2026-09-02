"""Окно выбора бренда: выпадающее меню + предпросмотр шаблона."""
from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QWidget,
)

from grafmaster.core import brand_catalog


class BrandSelector(QDialog):
    """Выбор бренда (шаблон берётся из assets/templates по имени файла)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Выбор бренда")
        self.setModal(True)
        self.resize(360, 520)

        root = QVBoxLayout(self)
        root.addWidget(QLabel("Бренд (шаблон карточки):"))
        self.combo = QComboBox()
        self.combo.addItems(brand_catalog.discover_brands())
        self.combo.currentTextChanged.connect(self._preview)
        root.addWidget(self.combo)

        root.addWidget(QLabel("Предпросмотр шаблона:"))
        self.preview = QSvgWidget()
        self.preview.setFixedSize(270, 360)
        root.addWidget(self.preview, 1, Qt.AlignHCenter)

        box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        root.addWidget(box)

        self._preview(self.combo.currentText())

    def _preview(self, brand: str) -> None:
        path = brand_catalog.template_for_brand(brand)
        if path:
            self.preview.load(str(path))

    @staticmethod
    def get_brand(parent: QWidget | None = None) -> str | None:
        dlg = BrandSelector(parent)
        if dlg.exec() == QDialog.Accepted:
            return dlg.combo.currentText()
        return None
