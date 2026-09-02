"""Импорт шаблонов пользователя из Desktop/Шаблоны в assets/templates."""
import shutil
from pathlib import Path

SRC = Path(r"C:\Users\Anna\Desktop\Шаблоны")
DST = Path(r"C:\Users\Anna\.cline\data\workspaces\chat\GrafMaster\assets\templates")

if not SRC.exists():
    print("SRC NOT FOUND")
    raise SystemExit

if DST.exists():
    shutil.rmtree(DST)
DST.mkdir(parents=True)

for item in SRC.iterdir():
    if item.is_dir():
        shutil.copytree(item, DST / item.name)
    else:
        shutil.copy2(item, DST / item.name)
    print("COPIED:", item.name)

print("DONE ->", DST)
