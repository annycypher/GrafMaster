"""Список файлов в папке Desktop/Шаблоны."""
from pathlib import Path

base = Path(r"C:\Users\Anna\Desktop\Шаблоны")
print("EXISTS:", base.exists())
if base.exists():
    for p in sorted(base.rglob("*")):
        if p.is_dir():
            print("[DIR]", str(p.relative_to(base)))
        else:
            print(p.name, "|", p.stat().st_size, "bytes |", p.suffix)
