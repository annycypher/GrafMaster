"""Окно «Товар по ссылке»: вставка ссылок и извлечение данных (Этап 2).

Извлечение выполняется в фоновом потоке: скачивание страницы,
название + характеристики (парсер Bitrix), скачивание фото.
"""
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout,
    QWidget,
)

from grafmaster.core import link_parser

OUTPUT_PHOTOS = Path(__file__).resolve().parents[3] / "output" / "photos"


class _ExtractWorker(QThread):
    done = Signal(str)

    def __init__(self, links: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.links = links

    def run(self) -> None:
        lines: list[str] = []
        for url in self.links:
            try:
                data = link_parser.extract_product(url)
                photo = None
                if data.images:
                    folder = OUTPUT_PHOTOS / link_parser.safe_dir_name(data.name)
                    photo = link_parser.download_image(data.images[0], folder)
                lines.append(f"ТОВАР: {data.name}")
                lines.append(f"Характеристик: {len(data.characteristics)}")
                for title, value in data.characteristics[:12]:
                    lines.append(f"  • {title}: {value}")
                if len(data.characteristics) > 12:
                    lines.append(f"  … и ещё {len(data.characteristics) - 12} шт.")
                lines.append(f"Фото: {photo}" if photo else "Фото: не найдено")
                lines.append("")
            except Exception as exc:  # noqa: BLE001
                lines.append(f"ОШИБКА для {url}\n  {exc}\n")
        self.done.emit("\n".join(lines))


class ProductLinkDialog(QDialog):
    """Отдельное окно: ссылки на товары -> извлечение название/характеристики/фото."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Товар по ссылке")
        self.setModal(True)
        self.resize(620, 580)

        root = QVBoxLayout(self)
        root.addWidget(QLabel("Вставьте ссылки на товары (по одной на строку):"))
        self.inp_links = QPlainTextEdit()
        self.inp_links.setPlaceholderText(
            "https://kumtigey.ru/catalog/...\nhttps://kumtigey.ru/catalog/...")
        root.addWidget(self.inp_links, 1)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        root.addWidget(self.status)

        self.result = QPlainTextEdit()
        self.result.setReadOnly(True)
        self.result.setPlaceholderText(
            "Здесь появится извлечённое: название, характеристики, фото…")
        root.addWidget(self.result, 1)

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
        self.btn_extract.setEnabled(False)
        self.status.setText(f"Извлекаю {len(links)} ссылок… (страница + фото)")
        self.result.setPlainText("")
        self._worker = _ExtractWorker(links)
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_done(self, text: str) -> None:
        self.result.setPlainText(text)
        self.status.setText("Готово. Проверьте результат; далее товары попадут в список.")
        self.btn_extract.setEnabled(True)

