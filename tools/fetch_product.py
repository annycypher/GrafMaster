"""Разведка страницы товара: структура, JSON-LD, фото, характеристики."""
import re
import urllib.request
from pathlib import Path

URL = ("https://kumtigey.ru/catalog/sadovo_ogorodnaya_tekhnika/"
       "pily_tsepnye/benzopila_geos_max_csp346_227520/?ysclid=mtihisz85j322957550")

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
Path(r"C:\Users\Anna\.cline\data\workspaces\chat\GrafMaster\tools\_page.html").write_text(html, encoding="utf-8")
print("HTML len:", len(html))

m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
print("TITLE:", m.group(1).strip() if m else None)

for i, block in enumerate(re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S | re.I)):
    print("--- JSON-LD", i, "len", len(block.strip()))
    print(block.strip()[:1800])
    if i >= 2:
        break

imgs = re.findall(r'<img[^>]*src="([^"]+)"', html, re.I)
print("IMGS:", imgs[:15])
og = re.findall(r'<meta[^>]*(?:property|name)="(og:image|description|og:title)"[^>]*content="([^"]*)"', html, re.I)
print("OG:", og[:5])
