"""Точка входа приложения GrafMaster."""
import sys

from PySide6.QtWidgets import QApplication

from grafmaster.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("GrafMaster")
    app.setOrganizationName("GrafMaster")
    window = MainWindow()
    window.show()
    return app.exec()
