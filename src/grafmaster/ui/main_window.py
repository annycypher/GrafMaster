"""Главное окно GrafMaster: шапка, вкладки, темы, статус-бар."""
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPushButton, \
    QTabWidget, QVBoxLayout, QWidget

from grafmaster import theme
from grafmaster.ui.home_tab import HomeTab
from grafmaster.ui.project_tab import ProjectTab
from grafmaster.ui.settings_tab import SettingsTab
from grafmaster.ui.templates_tab import TemplatesTab


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GrafMaster — генератор инфографики")
        self.resize(1280, 820)
        self._dark = True
        self._a11y = False

        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- шапка ----
        head = QHBoxLayout()
        head.setContentsMargins(12, 8, 12, 8)
        logo = QLabel("🎨 GrafMaster")
        logo.setStyleSheet("font-size: 17px; font-weight: 800;")
        head.addWidget(logo)
        head.addSpacing(20)
        chip = QLabel("🔑 DeepSeek: подключён")
        chip.setObjectName("muted")
        head.addWidget(chip)
        head.addStretch(1)
        self.btn_theme = QPushButton("☀️")
        self.btn_theme.setFixedSize(38, 38)
        self.btn_theme.setToolTip("Светлая / тёмная тема")
        self.btn_theme.clicked.connect(self.toggle_theme)
        head.addWidget(self.btn_theme)
        self.btn_a11y = QPushButton("👓 Aa")
        self.btn_a11y.setToolTip("Версия для слабовидящих")
        self.btn_a11y.clicked.connect(self.toggle_a11y)
        head.addWidget(self.btn_a11y)
        root.addLayout(head)

        # ---- вкладки ----
        self.tabs = QTabWidget()
        self.home = HomeTab()
        self.project = ProjectTab()
        self.templates = TemplatesTab()
        self.settings = SettingsTab()
        self.tabs.addTab(self.home, "Главная")
        self.tabs.addTab(self.project, "Проект карточек")
        self.tabs.addTab(self.templates, "Шаблоны")
        self.tabs.addTab(self.settings, "Настройки")
        root.addWidget(self.tabs, 1)

        self.setCentralWidget(central)
        self.statusBar().showMessage("Готов к работе · Движки: Pillow (сборка), rembg (фон)")

        self.apply_theme()

    def apply_theme(self) -> None:
        palette = theme.DARK if self._dark else theme.LIGHT
        if self._a11y:
            palette = theme.A11Y
        self.setStyleSheet(theme.build_qss(palette, a11y=self._a11y))
        self.btn_theme.setText("🌙" if not self._dark else "☀️")

    def toggle_theme(self) -> None:
        self._dark = not self._dark
        self.apply_theme()

    def toggle_a11y(self) -> None:
        self._a11y = not self._a11y
        self.apply_theme()
        self.btn_a11y.setStyleSheet(
            "border: 2px solid #a855f7; font-weight: 800;" if self._a11y else "")
