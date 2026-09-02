"""Скачивает 20 шрифтов (Google Fonts, OFL/Apache — свободное использование)
и делает из них статические TTF (Regular) с поддержкой кириллицы."""
import json
import urllib.request
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

DST = Path(r"C:\Users\Anna\.cline\data\workspaces\chat\GrafMaster\assets\fonts")

# (Имя в каталоге, папка в google/fonts)
FONTS = [
    ("Russo One", "ofl/russoone"),
    ("Montserrat", "ofl/montserrat"),
    ("Open Sans", "ofl/opensans"),
    ("Roboto", "ofl/roboto"),
    ("Roboto Condensed", "ofl/robotocondensed"),
    ("Oswald", "ofl/oswald"),
    ("Play", "ofl/play"),
    ("Exo 2", "ofl/exo2"),
    ("PT Sans", "ofl/ptsans"),
    ("Lora", "ofl/lora"),
    ("Merriweather", "ofl/merriweather"),
    ("Playfair Display", "ofl/playfairdisplay"),
    ("Comfortaa", "ofl/comfortaa"),
    ("Jura", "ofl/jura"),
    ("Cuprum", "ofl/cuprum"),
    ("Forum", "ofl/forum"),
    ("Caveat", "ofl/caveat"),
    ("Lobster", "ofl/lobster"),
    ("PT Serif", "ofl/ptserif"),
    ("Raleway", "ofl/raleway"),
]

API = "https://api.github.com/repos/google/fonts/contents/{}"


def pick_ttf(files: list[dict]) -> str | None:
    """Выбирает НЕ-italic файл: обычный (Regular) или вариативный [wght]."""
    ttfs = [f["name"] for f in files if f["name"].lower().endswith(".ttf")]
    ttfs = [n for n in ttfs if "italic" not in n.lower() and "bold" not in n.lower()]
    if not ttfs:
        return None
    for prefer in ("regular", "Regular"):
        for name in ttfs:
            if prefer in name:
                return name
    for name in ttfs:
        if "wght" in name:
            return name
    return ttfs[0]


def to_static(font: TTFont, weight: int = 400) -> TTFont:
    if "fvar" not in font:
        return font
    axes = {a.axisTag: round(float(a.defaultValue)) for a in font["fvar"].axes}
    if "wght" in axes:
        axes["wght"] = weight
    return instantiateVariableFont(font, axes, inplace=False)


def main() -> None:
    for display, repo_dir in FONTS:
        safe = display.replace(" ", "")
        out = DST / f"{safe}-Regular.ttf"
        if out.exists():
            print(f"SKIP exists: {display}")
            continue
        try:
            req = urllib.request.Request(API.format(repo_dir),
                                         headers={"User-Agent": "GrafMaster"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                listing = json.loads(resp.read().decode("utf-8"))
            name = pick_ttf(listing)
            if name is None:
                print(f"FAIL no ttf: {display}")
                continue
            raw_url = f"https://raw.githubusercontent.com/google/fonts/main/{repo_dir}/{name}"
            urllib.request.urlretrieve(raw_url, str(DST / "_raw.ttf"))
            font = TTFont(str(DST / "_raw.ttf"))
            static = to_static(font, 400)
            static.save(str(out))
            print(f"OK: {display} <- {name} ({out.stat().st_size} bytes)")
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL: {display}: {exc}")
    (DST / "_raw.ttf").unlink(missing_ok=True)
    print("DONE")


if __name__ == "__main__":
    main()
