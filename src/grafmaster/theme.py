"""Темы интерфейса GrafMaster: неоновая фиолетовая, светлая, для слабовидящих."""
from string import Template

# Тёмная неоновая фиолетовая (по умолчанию)
DARK = {
    "bg": "#0d0714", "panel": "#150b20", "panel2": "#1c112e",
    "line": "#39274f", "text": "#f1eaff", "muted": "#a58fc9",
    "accent": "#a855f7", "accent2": "#c084fc",
    "neon1": "#8b5cf6", "neon2": "#a855f7",
    "ghost_text": "#dccff5", "ghost_border": "#513a77",
}

# Светлая
LIGHT = {
    "bg": "#f4f6fb", "panel": "#ffffff", "panel2": "#eef1f6",
    "line": "#d7dce6", "text": "#111827", "muted": "#5b6472",
    "accent": "#7c3aed", "accent2": "#6d28d9",
    "neon1": "#8b5cf6", "neon2": "#7c3aed",
    "ghost_text": "#1f2937", "ghost_border": "#d7dce6",
}

# Для слабовидящих: высокий контраст, фиолетовые контуры
A11Y = {
    "bg": "#000000", "panel": "#000000", "panel2": "#0e0e0e",
    "line": "#a855f7", "text": "#ffffff", "muted": "#d7c9f2",
    "accent": "#a855f7", "accent2": "#c084fc",
    "neon1": "#a855f7", "neon2": "#a855f7",
    "ghost_text": "#ffffff", "ghost_border": "#a855f7",
}

_QSS = Template("""
QMainWindow, QDialog { background: $bg; }
QWidget { color: $text; font-family: "Segoe UI", Arial; font-size: 13px; }
QLabel#muted { color: $muted; }
QTabWidget::pane { border: 1px solid $line; background: $panel; }
QTabBar::tab { background: transparent; color: $muted; padding: 8px 18px; font-size: 14px; }
QTabBar::tab:hover { color: $text; }
QTabBar::tab:selected { color: $accent2; border-bottom: 2px solid $accent; font-weight: 600; }
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 $neon1, stop:1 $neon2);
    color: #ffffff; border: 1px solid $accent; border-radius: 12px;
    padding: 8px 14px; font-weight: 600;
}
QPushButton:hover { border: 1px solid $accent2; }
QPushButton:pressed { padding-top: 9px; padding-bottom: 7px; }
QPushButton[ghost="true"] {
    background: $panel2; color: $ghost_text; border: 1px solid $ghost_border; font-weight: 400;
}
QPushButton[checked="true"] { border: 2px solid $accent2; }
QLineEdit, QComboBox, QListWidget, QScrollArea, QPlainTextEdit {
    background: $panel2; color: $text; border: 1px solid $line;
    border-radius: 10px; padding: 7px 10px; selection-background-color: $accent;
}
QListWidget::item { padding: 8px 10px; border-radius: 8px; margin: 2px; }
QListWidget::item:selected { background: $accent; color: #ffffff; }
QListWidget::item:hover { background: $panel2; }
QScrollBar:vertical { background: transparent; width: 10px; }
QScrollBar::handle:vertical { background: $line; border-radius: 5px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QStatusBar { background: $panel; border-top: 1px solid $line; }
QSplitter::handle { background: $line; }
""")

_A11Y_QSS = Template("""
QWidget { font-size: 16px; }
QTabBar::tab { font-size: 18px; padding: 10px 20px; }
QPushButton { border: 2px solid $accent; padding: 10px 16px; }
QPushButton[ghost="true"] { border: 2px solid $accent; }
QListWidget::item { padding: 10px 12px; }
""")


def build_qss(palette: dict, a11y: bool = False) -> str:
    """Собирает QSS-стиль приложения по палитре."""
    qss = _QSS.substitute(**palette)
    if a11y:
        qss += _A11Y_QSS.substitute(**palette)
    return qss
