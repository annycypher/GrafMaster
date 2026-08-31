"""Вкладка «Главная»: режимы, лента карточек, свойства, экспорт."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QColorDialog, QComboBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QScrollArea, QSplitter,
    QVBoxLayout, QWidget,
)

from grafmaster.ui.icon_library import IconLibraryDialog
from grafmaster.ui.widgets import CardView, SmallCard, make_ghost

TEXTS = [
    "Мощность: 2200 Вт\nЗагрузка: 7 кг",
    "Загрузка: 7 кг",
    "Обороты: 1400 об/мин",
    "Класс: A+++",
    "Шум: 52 дБ",
    "Габариты: 60×60×85 см",
    "Гарантия: 3 года",
]
ICONS = ["⚡", "💧", "🌀", "❄️", "🔥", "⭐", "✅"]


class HomeTab(QWidget):
    """Главный экран по макету «Вариант 6» (GrafMaster Neon)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._card_index = 0
        self._plate = "Стиральная машина"
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        # ---- верхняя панель: режимы + экспорт ----
        bar = QHBoxLayout()
        self.mode_folder = QPushButton("📁 Из папки")
        self.mode_online = QPushButton("🌐 Онлайн")
        for btn in (self.mode_folder, self.mode_online):
            btn.setCheckable(True)
            bar.addWidget(btn)
        self.mode_folder.setChecked(True)
        self.mode_folder.clicked.connect(lambda: self._set_mode("folder"))
        self.mode_online.clicked.connect(lambda: self._set_mode("online"))

        self.btn_folder = make_ghost(QPushButton("Выбрать папку"))
        self.btn_folder.clicked.connect(self._pick_folder)
        bar.addWidget(self.btn_folder)
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Название товара для поиска...")
        self.inp_search.hide()
        bar.addWidget(self.inp_search)
        self.btn_search = make_ghost(QPushButton("Найти"))
        self.btn_search.hide()
        bar.addWidget(self.btn_search)

        bar.addStretch(1)
        for txt in ("Скачать JPG", "Скачать PDF", "Скачать SVG", "Скачать .fig"):
            bar.addWidget(make_ghost(QPushButton(txt)))
        bar.addWidget(QPushButton("Вставить в Figma"))
        root.addLayout(bar)

        # ---- рабочая область ----
        split = QSplitter(Qt.Horizontal)

        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        self.list_products = QListWidget()
        for name in ("Стиральная машина · 7", "Холодильник · 7",
                     "Микроволновка · 7", "Пылесос · 7", "Утюг · 7"):
            self.list_products.addItem(QListWidgetItem(name))
        lv.addWidget(self.list_products, 1)
        lv.addWidget(make_ghost(QPushButton("Загрузить Excel")))
        split.addWidget(left)

        center = QWidget()
        cv = QVBoxLayout(center)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.addStretch(1)

        self.card = CardView()
        cv.addWidget(self.card, 0, Qt.AlignHCenter)

        arrows = QHBoxLayout()
        self.btn_prev = make_ghost(QPushButton("←"))
        self.btn_next = make_ghost(QPushButton("→"))
        self.btn_prev.clicked.connect(lambda: self._set_card(self._card_index - 1))
        self.btn_next.clicked.connect(lambda: self._set_card(self._card_index + 1))
        arrows.addStretch(1)
        arrows.addWidget(self.btn_prev)
        arrows.addWidget(self.btn_next)
        arrows.addStretch(1)
        cv.addLayout(arrows)

        self.lbl_counter = QLabel("Карточка 1 из 7 · 900×1200")
        self.lbl_counter.setObjectName("muted")
        self.lbl_counter.setAlignment(Qt.AlignCenter)
        cv.addWidget(self.lbl_counter)

        # лента из 7 карточек с прокруткой
        strip_host = QScrollArea()
        strip_host.setWidgetResizable(True)
        strip_host.setFixedHeight(150)
        strip_w = QWidget()
        sw = QHBoxLayout(strip_w)
        sw.setContentsMargins(4, 4, 4, 4)
        sw.setSpacing(8)
        self.mini_cards: list[SmallCard] = []
        for i in range(7):
            mini = SmallCard(i)
            mini.clicked.connect(self._set_card)
            sw.addWidget(mini)
            self.mini_cards.append(mini)
        sw.addStretch(1)
        strip_host.setWidget(strip_w)
        cv.addWidget(strip_host)

        self.lbl_hint = QLabel(
            "💡 Клик по карточке в ленте — выбор. В реальном приложении: "
            "клик по объекту — перемещение, двойной клик по тексту — "
            "редактирование, клик по иконке — библиотека иконок.")
        self.lbl_hint.setObjectName("muted")
        self.lbl_hint.setWordWrap(True)
        self.lbl_hint.setAlignment(Qt.AlignCenter)
        cv.addWidget(self.lbl_hint)
        cv.addStretch(1)
        split.addWidget(center)

        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(8, 8, 8, 8)
        rv.addWidget(QLabel("СВОЙСТВА"))
        rv.addWidget(QLabel("Название"))
        self.inp_name = QLineEdit(self._plate)
        rv.addWidget(self.inp_name)
        rv.addWidget(QLabel("Характеристика"))
        self.inp_char = QLineEdit("Мощность: 2200 Вт")
        rv.addWidget(self.inp_char)
        rv.addWidget(QLabel("Цвет плашки"))
        self.btn_color = QPushButton("Выбрать цвет")
        self.btn_color.clicked.connect(self._pick_color)
        rv.addWidget(self.btn_color)
        rv.addWidget(QLabel("Шрифт"))
        self.combo_font = QComboBox()
        self.combo_font.addItems(["Inter", "Manrope", "Rubik"])
        rv.addWidget(self.combo_font)
        rv.addWidget(QLabel("Иконка"))
        self.btn_icon = QPushButton("🎨 Открыть библиотеку иконок")
        self.btn_icon.clicked.connect(self._open_icons)
        rv.addWidget(self.btn_icon)
        rv.addStretch(1)
        rv.addWidget(QLabel("ЭКСПОРТ"))
        for txt in ("PNG · 900×1200", "JPG · 900×1200", "PDF · 7 стр."):
            rv.addWidget(make_ghost(QPushButton(txt)))
        split.addWidget(right)

        split.setSizes([220, 640, 260])
        root.addWidget(split, 1)

        # ---- нижняя панель движков ----
        eng = QHBoxLayout()
        eng.addWidget(QLabel("Движки:"))
        for name, on in (("Pillow", True), ("Inkscape", False),
                         ("PS/Corel", False), ("rembg", True), ("SAM2", False)):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setChecked(on)
            eng.addWidget(btn)
        eng.addStretch(1)
        self.lbl_queue = QLabel("Очередь: 5 из 14")
        self.lbl_queue.setObjectName("muted")
        eng.addWidget(self.lbl_queue)
        root.addLayout(eng)

        self._set_card(0)

    # ---------- действия ----------

    def _set_mode(self, mode: str) -> None:
        online = mode == "online"
        self.mode_folder.setChecked(not online)
        self.mode_online.setChecked(online)
        self.btn_folder.setVisible(not online)
        self.inp_search.setVisible(online)
        self.btn_search.setVisible(online)

    def _pick_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку с материалами")
        if folder:
            self.lbl_counter.setText(f"Папка: {folder}")

    def _pick_color(self) -> None:
        color = QColorDialog.getColor()
        if color.isValid():
            self.btn_color.setStyleSheet(f"background: {color.name()}; color: #fff;")

    def _open_icons(self) -> None:
        icon = IconLibraryDialog.get_icon(self)
        if icon:
            self._set_icon(icon)

    def _set_icon(self, icon: str) -> None:
        ICONS[self._card_index] = icon
        self._set_card(self._card_index)

    def _set_card(self, index: int) -> None:
        index = (index + 7) % 7
        self._card_index = index
        self.card.set_content(self._plate, TEXTS[index], ICONS[index])
        self.lbl_counter.setText(f"Карточка {index + 1} из 7 · 900×1200")
        for i, mini in enumerate(self.mini_cards):
            mini.set_selected(i == index)

