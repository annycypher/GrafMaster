"""Окно «Товар по ссылке»: вставка ссылок и извлечение данных (Этап 2/7).

Сейчас — каркас: окно с полем для ссылок и кнопкой «Извлечь данные».
Модуль «Извлечение по ссылке» (скачивание страницы + DeepSeek + фото)
будет подключён на следующем этапе.
"""
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout,
    QWidget,
)


class ProductLinkDialog(QDialog):
    """Отдельное окно: вставьте ссылку на товар -> извлеките данные."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Товар по ссылке")
        self.setModal(True)
        self.resize(560, 420)

        root = QVBoxLayout(self)
        root.addWidget(QLabel("Вставьте ссылки на товары (по одной на строку):"))
        self.inp_links = QPlainTextEdit()
        self.inp_links.setPlaceholderText(
            "https://kumtigey.ru/catalog/...\n"
            "https://kumtigey.ru/catalog/...")
        root.addWidget(self.inp_links, 1)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        root.addWidget(self.status)

        btns = QHBoxLayout()
        self.btn_extract = QPushButton("Извлечь данные")
        self.btn_extract.clicked.connect(self._extract)
        btns.addWidget(self.btn_extract)
        self.btn_close = QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.reject)
        btns.addWidget(self.btn_close)
        root.addLayout(btns)

    def links(self) -> list[str]:
        return [ln.strip() for ln in self.inp_links.toPlainText().splitlines() if ln.strip()]

    def _extract(self) -> None:
        links = self.links()
        if not links:
            self.status.setText("⚠ Вставьте хотя бы одну ссылку.")
            return
        # Этап 2.5: скачать страницу -> DeepSeek (название + характеристики)
        # -> скачать фото -> заполнить шаблон Excel.
        self.status.setText(
            f"Получено ссылок: {len(links)}.\n"
            "Модуль «Извлечение по ссылке» (скачивание страницы + DeepSeek + фото) "
            "будет подключён на следующем этапе.")
