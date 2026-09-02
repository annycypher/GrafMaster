"""Извлекает характеристики из сохранённой страницы (Bitrix)."""
import re
from pathlib import Path

html = Path(r"C:\Users\Anna\.cline\data\workspaces\chat\GrafMaster\tools\_page.html").read_text(encoding="utf-8")

# Ищем заголовок «Характеристики» и печатаем контекст после него
for kw in ("Характеристики", "характеристики"):
    idx = html.find(kw)
    if idx != -1:
        print("=== найдено", kw, "at", idx)
        print(html[idx:idx + 3500].replace("\n", " ")[:3500])
        break

# Пары td->td (характеристики в таблицах Bitrix)
pairs = re.findall(r"<td[^>]*>\s*(?:<[^>]+>)*([^<>]{2,80}?)(?:<[^>]+>)*\s*</td>\s*<td[^>]*>\s*(?:<[^>]+>)*([^<>]{2,160}?)(?:<[^>]+>)*\s*</td>", html, re.S)
print("\n=== PAIRS (first 40):")
for p in pairs[:40]:
    print("  ", p[0].strip()[:50], "=>", p[1].strip()[:80])
