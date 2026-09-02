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

from grafmaster.core import card_builder, link_parser

OUTPUT_PHOTOS = Path(__file__).resolve().parents[3] / "output" / "photos"
OUTPUT_CARDS = Path(__file__).resolve().parents[3] / "output" / "cards"


class _ExtractWorker(QThread):
    done = Signal(str, object)  # сводка + список ProductData

    def __init__(self, links: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.links = links

    def run(self) -> None:
        lines: list[str] = []
        products: list[link_parser.ProductData] = []
        for url in self.links:
            try:
                data = link_parser.extract_product(url)
                products.append(data)
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
        self.done.emit("\n".join(lines), products)


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
        self.btn_cards = QPushButton("Собрать карточки (7 шт)")
        self.btn_cards.setEnabled(False)
        self.btn_cards.clicked.connect(self._build_cards)
        btns.addWidget(self.btn_cards)
        self.btn_close = QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.reject)
        btns.addWidget(self.btn_close)
        root.addLayout(btns)

        self._products: list[link_parser.ProductData] = []

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

    def _on_done(self, text: str, products: list[link_parser.ProductData]) -> None:
        self._products = products
        self.result.setPlainText(text)
        self.btn_cards.setEnabled(bool(products))
        self.status.setText(
            "Готово. Можно собрать карточки — кнопка «Собрать карточки (7 шт)».")
        self.btn_extract.setEnabled(True)

    def _build_cards(self) -> None:
        if not self._products:
            return
        lines: list[str] = []
        for data in self._products:
            photo = None
            if data.images:
                folder = OUTPUT_PHOTOS / link_parser.safe_dir_name(data.name)
                photo = link_parser.download_image(data.images[0], folder)
            chars = card_builder.pick_chars(data.characteristics)
            out = OUTPUT_CARDS / link_parser.safe_dir_name(data.name)
            files = card_builder.build_set(data.name, chars, photo, out)
            lines.append(f"{data.name}: создано {len(files)} карточек → {out}")
        self.result.appendPlainText("\n" + "\n".join(lines))
        self.status.setText("Карточки собраны. Пути — в поле результата.")

