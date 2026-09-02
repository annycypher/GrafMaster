"""Список файлов в папке с примерами карточек (Desktop/Пример)."""
from pathlib import Path

base = Path(r"C:\Users\Anna\Desktop\Пример")
print("EXISTS:", base.exists())
if base.exists():
    for p in sorted(base.rglob("*")):
        kind = "<DIR>" if p.is_dir() else f"{p.stat().st_size} bytes"
        print(f"{p.name} | {kind} | {p.suffix}")
