"""Окно «Шаблон по вектору (SVG)»: загрузка, анализ слоёв, порядок наложения.

На основе SVG-макета строится шаблон карточки: нижний слой — фото на белом,
средние — иконки и характеристики, верхний — векторная графика и название.
"""
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QFileDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QSplitter, QVBoxLayout, QWidget,
)

from grafmaster.core import svg_parser

KIND_NAMES = {
    "bg": "Фон (белый)",
    "title": "Название (крупно)",
    "photo": "Фото товара",
    "text": "Текст/характеристика",
    "icon": "Иконка",
    "vector": "Векторная графика",
}


class TemplateWindow(QWidget):
    """Окно загрузки векторного примера и анализа его структуры."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Шаблон по вектору (SVG)")
        self.resize(1080, 720)
        self.template: svg_parser.SvgTemplate | None = None

        root = QVBoxLayout(self)
        bar = QHBoxLayout()
        self.btn_open = QPushButton("Загрузить SVG-шаблон")
        self.btn_open.clicked.connect(self._load)
        bar.addWidget(self.btn_open)
        self.info = QLabel(
            "Загрузите векторный макет (SVG): название сверху, фото, "
            "характеристики с иконками, вектор поверх.")
        bar.addWidget(self.info, 1)
        root.addLayout(bar)

        split = QSplitter()
        self.preview = QSvgWidget()
        split.addWidget(self.preview)

        right = QWidget()
        rv = QVBoxLayout(right)
        rv.addWidget(QLabel("Слои (снизу вверх = порядок наложения):"))
        self.layers = QListWidget()
        rv.addWidget(self.layers, 1)
        self.detail = QLabel("")
        self.detail.setWordWrap(True)
        rv.addWidget(self.detail)
        split.addWidget(right)
        split.setSizes([680, 380])
        root.addWidget(split, 1)

    def _load(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите SVG-шаблон", "", "SVG (*.svg)")
        if not path:
            return
        try:
            tmpl = svg_parser.parse_svg(path)
        except Exception as exc:  # noqa: BLE001
            self.info.setText(f"⚠ Не удалось разобрать SVG: {exc}")
            return
        self.template = tmpl
        self.preview.load(path)
        self.layers.clear()
        for layer in tmpl.layers:
            kind = KIND_NAMES.get(layer.kind, layer.kind)
            if layer.kind == "photo":
                label = f"{layer.z}: Фото товара ({int(layer.w)}×{int(layer.h)})"
            elif layer.text:
                label = f"{layer.z}: {kind} — «{layer.text}»"
            else:
                label = f"{layer.z}: {kind}"
            self.layers.addItem(QListWidgetItem(label))
        self.info.setText(f"Шаблон: {path}")
        photo = tmpl.photo
        if photo:
            self.detail.setText(
                f"Название: «{tmpl.name}»\n"
                f"Зона фото: ({int(photo.x)}, {int(photo.y)}, "
                f"{int(photo.w)}×{int(photo.h)})\n"
                f"Слоёв: {len(tmpl.layers)}")
        else:
            self.detail.setText(
                f"Название: «{tmpl.name}»\nЗона фото: не найдена\n"
                f"Слоёв: {len(tmpl.layers)}")
