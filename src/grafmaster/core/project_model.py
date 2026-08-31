"""Формат проекта GrafMaster (.gmproj) — JSON: слои, стили, палитра.

Это «редактируемый» формат (мини-Figma). Экспорт SVG/.fig — Этап 6.
"""
import json
from dataclasses import asdict, dataclass, field


@dataclass
class Layer:
    kind: str = "rect"       # rect | photo | text | icon | frame
    x: int = 0
    y: int = 0
    w: int = 900
    h: int = 200
    text: str = ""
    color: str = "#a855f7"
    font: str = "Inter"
    icon: str = ""


@dataclass
class Card:
    index: int = 1
    layers: list = field(default_factory=list)


@dataclass
class CardProject:
    product_name: str = ""
    cards: list = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, raw: str) -> "CardProject":
        data = json.loads(raw)
        data["cards"] = [Card(**c) for c in data.get("cards", [])]
        return cls(**data)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.to_json())

    @classmethod
    def load(cls, path: str) -> "CardProject":
        with open(path, encoding="utf-8") as fh:
            return cls.from_json(fh.read())
