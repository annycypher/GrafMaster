"""Окно общения с DeepSeek: чат + правки карточки в реальном времени."""
import json
import re

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextBrowser,
    QVBoxLayout, QWidget,
)

from grafmaster.core import deepseek


class _ChatWorker(QThread):
    done = Signal(str)

    def __init__(self, key: str, messages: list[dict],
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.key = key
        self.messages = messages

    def run(self) -> None:
        try:
            self.done.emit(deepseek.chat(self.key, self.messages))
        except Exception as exc:  # noqa: BLE001
            self.done.emit(f"⚠ Ошибка: {exc}")


class ChatWindow(QDialog):
    """Чат с DeepSeek; правки JSON-командами применяются к слоям шаблона."""

    def __init__(self, template=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("DeepSeek — ассистент GrafMaster")
        self.resize(540, 640)
        self.template = template  # SvgTemplate | None
        self.messages: list[dict] = [
            {"role": "system", "content": deepseek.system_prompt()}]

        root = QVBoxLayout(self)
        self.log = QTextBrowser()
        self.log.setOpenExternalLinks(True)
        root.addWidget(self.log, 1)

        row = QHBoxLayout()
        self.inp = QLineEdit()
        self.inp.setPlaceholderText("Например: сделай название красным, увеличь слой 3")
        self.inp.returnPressed.connect(self._send)
        row.addWidget(self.inp, 1)
        self.btn_send = QPushButton("Отправить")
        self.btn_send.clicked.connect(self._send)
        row.addWidget(self.btn_send)
        root.addLayout(row)

        self.key_status = QLabel("")
        root.addWidget(self.key_status)
        self._update_key_status()

    def _update_key_status(self) -> None:
        self.key_status.setText(
            "🔑 DeepSeek: подключён" if deepseek.get_key()
            else "⚠ Введите ключ DeepSeek: вкладка «Настройки» → поле API-ключа.")

    def _send(self) -> None:
        text = self.inp.text().strip()
        if not text:
            return
        if not deepseek.get_key():
            self.log.append("⚠ Ключ DeepSeek не задан. Настройки → поле API-ключа.")
            return
        self.messages.append({"role": "user", "content": text})
        self.log.append(f"<b>Вы:</b> {text}")
        self.inp.clear()
        self._worker = _ChatWorker(deepseek.get_key(), list(self.messages))
        self._worker.done.connect(self._on_answer)
        self._worker.start()

    def _on_answer(self, answer: str) -> None:
        self.messages.append({"role": "assistant", "content": answer})
        self.log.append(f"<b>DeepSeek:</b> {answer}")
        self._apply_edits(answer)

    def _apply_edits(self, answer: str) -> None:
        """Применяет JSON-правки {edits:[{layer, text?, fill?}]} к слоям шаблона."""
        if self.template is None:
            return
        m = re.search(r"\{[^{}]*\"edits\"[^{}]*\}", answer, re.S)
        if not m:
            return
        try:
            data = json.loads(m.group(0))
        except Exception:  # noqa: BLE001
            return
        applied = 0
        for edit in data.get("edits", []):
            idx = edit.get("layer")
            if isinstance(idx, int) and 0 <= idx < len(self.template.layers):
                layer = self.template.layers[idx]
                if "text" in edit:
                    layer.text = str(edit["text"])
                if "fill" in edit:
                    layer.fill = str(edit["fill"])
                applied += 1
                self.log.append(f"✅ Слой {idx}: {edit}")
        if applied:
            self.log.append(f"Применено правок: {applied} (в реальном времени).")
