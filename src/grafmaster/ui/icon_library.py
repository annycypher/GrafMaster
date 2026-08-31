"""Диалог «Библиотека иконок»: встроенные + место для своих (Этап 8)."""
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QVBoxLayout, QWidget,
)

from grafmaster.core.icons import BUILTIN_ICONS


class IconLibraryDialog(QDialog):
    """Окно выбора иконки. Возвращает выбранную через selected_icon()."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Библиотека иконок")
        self.setModal(True)
        self.resize(520, 480)
        self._selected = None
        self._mode = "builtin"

        root = QVBoxLayout(self)

        head = QHBoxLayout()
        head.addWidget(QLabel("🎨 Библиотека иконок"))
        head.addStretch(1)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск иконки...")
        self.search.setFixedWidth(220)
        self.search.textChanged.connect(self._rebuild)
        head.addWidget(self.search)
        root.addLayout(head)

        tabs = QHBoxLayout()
        self.tab_builtin = QPushButton("Встроенные")
        self.tab_mine = QPushButton("Мои (загружены)")
        self.tab_folder = QPushButton("Подключить папку…")
        for btn in (self.tab_builtin, self.tab_mine, self.tab_folder):
            btn.setCheckable(True)
            tabs.addWidget(btn)
        root.addLayout(tabs)
        self.tab_builtin.setChecked(True)
        self.tab_builtin.clicked.connect(lambda: self._activate(self.tab_builtin, "builtin"))
        self.tab_mine.clicked.connect(lambda: self._activate(self.tab_mine, "mine"))
        self.tab_folder.clicked.connect(lambda: self._activate(self.tab_folder, "folder"))

        self.grid_host = QWidget()
        self.grid_layout = QVBoxLayout(self.grid_host)
        self.grid_layout.setContentsMargins(0, 8, 0, 0)
        root.addWidget(self.grid_host, 1)

        box = QDialogButtonBox(QDialogButtonBox.Cancel)
        box.rejected.connect(self.reject)
        root.addWidget(box)

        self._rebuild()

    def _activate(self, btn: QPushButton, mode: str) -> None:
        for b in (self.tab_builtin, self.tab_mine, self.tab_folder):
            b.setChecked(b is btn)
        self._mode = mode
        self._rebuild()

    def _clear(self) -> None:
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def _rebuild(self) -> None:
        self._clear()
        if self._mode == "mine":
            self.grid_layout.addWidget(
                QLabel("Здесь появятся ваши иконки (PNG/SVG) из подключённой папки."))
            return
        if self._mode == "folder":
            self.grid_layout.addWidget(
                QLabel("Кнопка выбора папки с иконками появится на Этапе 8."))
            return
        query = self.search.text().strip().lower()
        icons = [i for i in BUILTIN_ICONS if query in i.lower()] if query else BUILTIN_ICONS
        grid = QGridLayout()
        for i, icon in enumerate(icons):
            btn = QPushButton(icon)
            btn.setFixedSize(48, 48)
            btn.clicked.connect(lambda _, ic=icon: self._pick(ic))
            grid.addWidget(btn, i // 6, i % 6)
        self.grid_layout.addLayout(grid)

    def _pick(self, icon: str) -> None:
        self._selected = icon
        self.accept()

    def selected_icon(self) -> str | None:
        return self._selected

    @staticmethod
    def get_icon(parent: QWidget | None = None) -> str | None:
        dlg = IconLibraryDialog(parent)
        if dlg.exec() == QDialog.Accepted:
            return dlg.selected_icon()
        return None
