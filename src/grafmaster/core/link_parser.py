"""Извлечение данных товара по ссылке (Этап 2): название, фото, характеристики.

Разбор страницы 1C-Bitrix (kumtigey.ru и подобные): характеристики в блоках
`js-prop-title` / `js-prop-value`, фото — в /upload/iblock/. Для других сайтов
подключается дополнительный парсер или DeepSeek (по ключу пользователя).
"""
import re
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin, urlparse

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


@dataclass
class ProductData:
    name: str
    url: str
    images: list = field(default_factory=list)
    characteristics: list = field(default_factory=list)  # (title, value)
    description: str = ""


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "ignore")


def _clean_name(raw: str) -> str:
    text = re.sub(r"\s+", " ", raw or "").strip()
    for sep in (" купить", " — купить", " – купить"):
        idx = text.find(sep)
        if idx != -1:
            text = text[:idx]
    return text.strip()


def extract_product(url: str) -> ProductData:
    html = fetch_html(url)

    def grab(pattern: str) -> str:
        m = re.search(pattern, html, re.I | re.S)
        return m.group(1).strip() if m else ""

    og_title = grab(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"')
    page_title = grab(r"<title>(.*?)</title>")
    name = _clean_name(og_title or page_title)

    og_desc = grab(r'<meta[^>]*property="og:description"[^>]*content="([^"]*)"')
    og_image = grab(r'<meta[^>]*property="og:image"[^>]*content="([^"]*)"')

    images: list[str] = [og_image] if og_image else []
    images += re.findall(r'<img[^>]*src="(/upload/(?!resize_cache)[^"]+)"', html, re.I)
    images = [urljoin(url, u) for u in images if u]
    seen: set[str] = set()
    unique = [u for u in images if not (u in seen or seen.add(u))]

    blocks = re.findall(
        r'<div class="properties__item[^"]*">.*?js-prop-title[^>]*>([^<]+)</div>'
        r'.*?js-prop-value[^>]*>([^<]+)</div>', html, re.S)
    chars = [(t.strip(), v.strip()) for t, v in blocks if t.strip()]

    return ProductData(name=name, url=url, images=unique,
                       characteristics=chars, description=og_desc)


def download_image(url: str, dest_dir: Path) -> Path | None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(urlparse(url).path).suffix or ".jpg"
    out = dest_dir / f"photo{suffix}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    if not data:
        return None
    out.write_bytes(data)
    return out


def safe_dir_name(name: str, limit: int = 60) -> str:
    safe = re.sub(r"[^\w\-]+", "_", name, flags=re.UNICODE).strip("_")
    return safe[:limit] or "product"
