"""Точка входа приложения GrafMaster."""
import sys

from PySide6.QtWidgets import QApplication

from grafmaster.core import fonts
from grafmaster.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("GrafMaster")
    app.setOrganizationName("GrafMaster")
    # Регистрируем шрифты с кириллицей (Inter/Rubik/Manrope) и ставим по умолчанию.
    fonts.register_fonts()
    app.setFont(fonts.default_font(10))
    window = MainWindow()
    window.show()
    return app.exec()
