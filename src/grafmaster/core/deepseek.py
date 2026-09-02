"""Клиент DeepSeek API (по ключу пользователя) + хранение ключа."""
import json
import urllib.request

from PySide6.QtCore import QSettings

API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"


def get_key() -> str:
    return str(QSettings("GrafMaster", "GrafMaster").value("deepseek_key", ""))


def set_key(key: str) -> None:
    QSettings("GrafMaster", "GrafMaster").setValue("deepseek_key", key.strip())


def chat(key: str, messages: list[dict], timeout: int = 60) -> str:
    """Отправляет диалог в DeepSeek и возвращает текст ответа."""
    body = {"model": MODEL, "messages": messages, "temperature": 0.3}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def system_prompt() -> str:
    return (
        "Ты — дизайн-ассистент GrafMaster. Помогаешь редактировать инфографику "
        "для маркетплейсов (карточки 900×1200). "
        "Если просят изменить карточку — возвращай JSON вида: "
        '{"edits":[{"layer":<номер слоя>, "text": "...", "fill": "#hex"}]}. '
        "Отвечай кратко по-русски.")
