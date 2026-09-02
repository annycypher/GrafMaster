"""Графический редактор: холст с перетаскиванием слоёв в реальном времени.

Часть 1: EditorCanvas — рендер SVG-шаблона + перетаскиваемые рамки слоёв
(фото, название, иконки, тексты). Изменения сохраняются в модели TemplateLayer.
"""
from PySide6.QtCore import QPoint, QRect, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QWidget

MOVE_KINDS = {"title", "photo", "icon", "text", "bg"}


class EditorCanvas(QWidget):
    layer_moved = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.template = None
        self.renderer: QSvgRenderer | None = None
        self._drag = -1
        self._last = QPoint()
        self.setMinimumSize(360, 480)

    def set_template(self, template, svg_path: str) -> None:
        self.template = template
        self.renderer = QSvgRenderer(svg_path)
        self._drag = -1
        self.update()

    def _scale(self) -> float:
        if not self.template:
            return 1.0
        return min(self.width() / self.template.width,
                   self.height() / self.template.height)

    def _origin(self) -> QPoint:
        if not self.template:
            return QPoint(0, 0)
        s = self._scale()
        w = int(self.template.width * s)
        h = int(self.template.height * s)
        return QPoint((self.width() - w) // 2, (self.height() - h) // 2)

    def _to_canvas(self, layer) -> QRect:
        s = self._scale()
        o = self._origin()
        return QRect(int(o.x() + layer.x * s), int(o.y() + layer.y * s),
                     int(max(8, layer.w * s)), int(max(8, layer.h * s)))

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#111318"))
        if not self.template or not self.renderer:
            return
        s = self._scale()
        o = self._origin()
        self.renderer.render(p, QRectF(o.x(), o.y(),
                                       self.template.width * s,
                                       self.template.height * s))
        for layer in self.template.layers:
            if layer.kind not in MOVE_KINDS:
                continue
            r = self._to_canvas(layer)
            p.setPen(QPen(QColor(168, 85, 247, 210), 2))
            p.setBrush(QColor(168, 85, 247, 36))
            p.drawRect(r)
            if layer.text:
                p.setPen(QColor("#f1eaff"))
                f = QFont(self.font())
                f.setPixelSize(12)
                p.setFont(f)
                p.drawText(r.adjusted(3, 3, -3, -3),
                           Qt.AlignLeft | Qt.AlignTop,
                           f"{layer.kind}: {layer.text}")

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if not self.template:
            return
        pos = event.position().toPoint()
        for layer in reversed(self.template.layers):
            if layer.kind not in MOVE_KINDS:
                continue
            if self._to_canvas(layer).contains(pos):
                self._drag = layer.z
                self._last = pos
                break

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._drag < 0 or not self.template:
            return
        pos = event.position().toPoint()
        d = pos - self._last
        s = self._scale()
        layer = next((l for l in self.template.layers if l.z == self._drag), None)
        if layer and s > 0:
            layer.x += d.x() / s
            layer.y += d.y() / s
            self._last = pos
            self.update()
            self.layer_moved.emit(layer.z)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._drag = -1


def render_template_to_image(template, svg_path: str, w: int = 900,
                             h: int = 1200) -> QImage:
    """Рендерит SVG-шаблон в PNG-изображение 900×1200."""
    renderer = QSvgRenderer(svg_path)
    img = QImage(w, h, QImage.Format_ARGB32)
    img.fill(Qt.white)
    p = QPainter(img)
    renderer.render(p, QRectF(0, 0, w, h))
    p.end()
    return img


# ---------- Часть 2: EditorWindow ----------
from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtGui import QColor  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QColorDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QSplitter, QVBoxLayout, QWidget,
)

from grafmaster.core import svg_parser  # noqa: E402
from grafmaster.ui.widgets import make_ghost  # noqa: E402

KIND_NAMES = {"bg": "Фон", "title": "Название", "photo": "Фото",
              "text": "Текст", "icon": "Иконка", "vector": "Вектор"}


class EditorWindow(QWidget):
    """Графический редактор: шаблон бренда + перетаскивание слоёв в реальном времени."""

    def __init__(self, brand: str, template_path: str,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Редактор — {brand}")
        self.resize(1240, 800)
        self.brand = brand
        self.template_path = template_path
        self.template = svg_parser.parse_svg(template_path)

        root = QVBoxLayout(self)
        bar = QHBoxLayout()
        bar.addWidget(QLabel("Бренд:"))
        self.lbl_brand = QLabel(brand)
        bar.addWidget(self.lbl_brand)
        bar.addSpacing(24)
        bar.addWidget(QLabel("Название товара:"))
        self.inp_name = QLineEdit()
        bar.addWidget(self.inp_name, 1)
        self.btn_export = QPushButton("Сохранить PNG (900×1200)")
        self.btn_export.clicked.connect(self._export)
        bar.addWidget(self.btn_export)
        self.btn_chat = make_ghost(QPushButton("💬 DeepSeek"))
        self.btn_chat.clicked.connect(self._open_chat)
        bar.addWidget(self.btn_chat)
        root.addLayout(bar)

        split = QSplitter(Qt.Horizontal)

        left = QWidget()
        lv = QVBoxLayout(left)
        lv.addWidget(QLabel("Слои (перетащите, чтобы изменить порядок наложения):"))
        self.layers = QListWidget()
        self.layers.setDragDropMode(QListWidget.InternalMove)
        self.layers.setDefaultDropAction(Qt.MoveAction)
        self.layers.model().rowsMoved.connect(self._sync_layers)
        self.layers.currentRowChanged.connect(self._select_layer)
        lv.addWidget(self.layers, 1)
        lv.addWidget(QLabel("Свойства слоя:"))
        self.inp_text = QLineEdit()
        self.inp_text.setPlaceholderText("Текст слоя…")
        self.inp_text.returnPressed.connect(self._apply_props)
        lv.addWidget(self.inp_text)
        self.btn_color = QPushButton("Цвет")
        self.btn_color.clicked.connect(self._pick_color)
        lv.addWidget(self.btn_color)
        split.addWidget(left)

        self.canvas = EditorCanvas()
        self.canvas.layer_moved.connect(lambda _z: self._refresh_props())
        split.addWidget(self.canvas)
        split.setSizes([320, 900])
        root.addWidget(split, 1)

        self.canvas.set_template(self.template, template_path)
        self._rebuild_layers()

    # ---------- слои ----------

    def _rebuild_layers(self) -> None:
        self.layers.blockSignals(True)
        self.layers.clear()
        for layer in self.template.layers:
            kind = KIND_NAMES.get(layer.kind, layer.kind)
            label = f"{layer.z}: {kind}"
            if layer.text:
                label += f" — «{layer.text}»"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, layer.z)
            self.layers.addItem(item)
        self.layers.blockSignals(False)

    def _sync_layers(self, *_args) -> None:
        """После перетаскивания в списке — обновляем z-порядок слоёв."""
        ordered = []
        for i in range(self.layers.count()):
            z = self.layers.item(i).data(Qt.UserRole)
            layer = next((l for l in self.template.layers if l.z == z), None)
            if layer:
                ordered.append(layer)
        if ordered:
            self.template.layers = ordered
            for i, layer in enumerate(ordered):
                layer.z = i
            self._rebuild_layers()
            self.canvas.update()

    def _select_layer(self, row: int) -> None:
        if row < 0:
            return
        z = self.layers.item(row).data(Qt.UserRole)
        layer = next((l for l in self.template.layers if l.z == z), None)
        if layer:
            self.inp_text.setText(layer.text)
            self.btn_color.setText(f"Цвет: {layer.fill}")

    def _apply_props(self) -> None:
        row = self.layers.currentRow()
        if row < 0:
            return
        z = self.layers.item(row).data(Qt.UserRole)
        layer = next((l for l in self.template.layers if l.z == z), None)
        if layer:
            layer.text = self.inp_text.text()
            self.canvas.update()
            self._rebuild_layers()
            self.layers.setCurrentRow(row)

    def _pick_color(self) -> None:
        row = self.layers.currentRow()
        if row < 0:
            return
        z = self.layers.item(row).data(Qt.UserRole)
        layer = next((l for l in self.template.layers if l.z == z), None)
        if layer is None:
            return
        start = QColor(layer.fill) if layer.fill.startswith("#") else QColor("#a855f7")
        color = QColorDialog.getColor(start, self)
        if color.isValid():
            layer.fill = color.name()
            self.btn_color.setText(f"Цвет: {layer.fill}")
            self.canvas.update()

    def _refresh_props(self) -> None:
        self._select_layer(self.layers.currentRow())

    # ---------- экспорт и чат ----------

    def _export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить PNG", f"{self.brand}_card.png", "PNG (*.png)")
        if not path:
            return
        img = render_template_to_image(self.template, self.template_path)
        img.save(path)
        self.setWindowTitle(f"Редактор — {self.brand} (сохранено: {path})")

    def _open_chat(self) -> None:
        from grafmaster.ui.chat_window import ChatWindow
        self._chat = ChatWindow(self.template)
        self._chat.show()
