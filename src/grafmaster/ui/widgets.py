"""Общие виджеты: карточка, мини-карточка, вспомогательные функции."""
from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QPushButton, QWidget


def make_ghost(btn: QPushButton) -> QPushButton:
    """Пометить кнопку как второстепенную (ghost)."""
    btn.setProperty("ghost", True)
    btn.style().unpolish(btn)
    btn.style().polish(btn)
    return btn


class CardView(QWidget):
    """Главная карточка 3:4 — область фото, плашка, текст, иконка."""

    clicked = Signal(int)

    def __init__(self, index: int = 0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.index = index
        self.plate = "Стиральная машина"
        self.text = "Мощность: 2200 Вт\nЗагрузка: 7 кг"
        self.icon = "⚡"
        self.setMinimumSize(240, 320)

    def set_content(self, plate: str, text: str, icon: str) -> None:
        self.plate, self.text, self.icon = plate, text, icon
        self.update()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        self.clicked.emit(self.index)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        big = self.width() >= 180
        r = QRectF(self.rect()).adjusted(2, 2, -2, -2)

        # фон карточки
        p.setBrush(QColor("#f4f0ff"))
        p.setPen(QPen(QColor("#c084fc"), 2))
        p.drawRoundedRect(r, 14, 14)

        # область фото
        photo_h = r.height() * 0.55
        p.setBrush(QColor("#ece5fa"))
        p.setPen(Qt.NoPen)
        p.drawRect(QRectF(r.left(), r.top(), r.width(), photo_h))
        p.setPen(QColor("#6d5a96"))
        f = QFont(self.font())
        f.setPixelSize(12 if big else 8)
        p.setFont(f)
        p.drawText(QRectF(r.left(), r.top(), r.width(), photo_h),
                   Qt.AlignCenter, "Фото товара (PNG)")

        # плашка
        plate_h = 42 if big else 18
        py = r.top() + photo_h
        grad = QLinearGradient(r.left(), py, r.right(), py)
        grad.setColorAt(0, QColor("#8b5cf6"))
        grad.setColorAt(1, QColor("#a855f7"))
        p.setBrush(grad)
        p.setPen(Qt.NoPen)
        p.drawRect(QRectF(r.left(), py, r.width(), plate_h))
        p.setPen(QColor("#ffffff"))
        f.setPixelSize(14 if big else 9)
        f.setBold(True)
        p.setFont(f)
        p.drawText(QRectF(r.left(), py, r.width(), plate_h), Qt.AlignCenter, self.plate)

        # текст
        ty = py + plate_h
        p.setPen(QColor("#3f3455"))
        f.setPixelSize(12 if big else 8)
        f.setBold(False)
        p.setFont(f)
        line_h = 18 if big else 11
        for i, line in enumerate(self.text.split("\n")[:2]):
            p.drawText(QRectF(r.left() + 8, ty + 8 + i * line_h, r.width() - 44, line_h),
                       Qt.AlignLeft | Qt.AlignVCenter, line)
        p.drawText(QRectF(r.left(), ty, r.width(), r.bottom() - ty),
                   Qt.AlignRight | Qt.AlignTop, self.icon + " ")


class SmallCard(QWidget):
    """Мини-карточка для ленты из 7 карточек одного товара."""

    clicked = Signal(int)

    def __init__(self, index: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.index = index
        self.selected = False
        self.setFixedSize(96, 128)

    def set_selected(self, value: bool) -> None:
        self.selected = value
        self.update()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        self.clicked.emit(self.index)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        p.setBrush(QColor("#f4f0ff"))
        p.setPen(QPen(QColor("#c084fc" if self.selected else "#c4b5e3"), 2 if self.selected else 1))
        p.drawRoundedRect(r, 8, 8)

        photo_h = r.height() * 0.55
        p.setBrush(QColor("#ece5fa"))
        p.setPen(Qt.NoPen)
        p.drawRect(QRectF(r.left(), r.top(), r.width(), photo_h))
        p.setPen(QColor("#6d5a96"))
        f = QFont(self.font())
        f.setPixelSize(8)
        p.setFont(f)
        p.drawText(QRectF(r.left(), r.top(), r.width(), photo_h), Qt.AlignCenter, "Фото")

        plate_h = 18
        py = r.top() + photo_h
        p.setBrush(QColor("#8b5cf6"))
        p.drawRect(QRectF(r.left(), py, r.width(), plate_h))
        p.setPen(QColor("#ffffff"))
        f.setPixelSize(8)
        f.setBold(True)
        p.setFont(f)
        p.drawText(QRectF(r.left(), py, r.width(), plate_h), Qt.AlignCenter, str(self.index + 1))
